import torch
from PIL import Image
from io import BytesIO
import base64
import os
import re
import sys
from transformers import CLIPProcessor, CLIPModel
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion, VectorType
from dotenv import load_dotenv
import uuid
import fitz 
from openai import OpenAI

# === Configuration ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
TEXT_INDEX_NAME = "text-embeddings"
IMAGE_INDEX_NAME = "image-embeddings"
FIGURES_DIR = "figures"
PDF_PATH = "images/somatosensory.pdf"

# Define separate namespaces for different content types
TEXT_NAMESPACE = "medical_text"
IMAGE_NAMESPACE = "medical_images"

client = OpenAI(api_key=OPENAI_API_KEY)
device = "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# === Initialize Pinecone ===
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize text index (1536 dimensions)
existing_indexes = [index.name for index in pc.list_indexes()]
if TEXT_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=TEXT_INDEX_NAME,
        dimension=1536,  # OpenAI embedding dimension
        metric="cosine",
        spec=ServerlessSpec(cloud=CloudProvider.AWS, region=AwsRegion.US_EAST_1),
        vector_type=VectorType.DENSE
    )
    print(f"Created text index: {TEXT_INDEX_NAME}")

# Initialize image index (512 dimensions)
if IMAGE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=IMAGE_INDEX_NAME,
        dimension=512,  # CLIP embedding dimension
        metric="cosine",
        spec=ServerlessSpec(cloud=CloudProvider.AWS, region=AwsRegion.US_EAST_1),
        vector_type=VectorType.DENSE
    )
    print(f"Created image index: {IMAGE_INDEX_NAME}")

# Connect to indexes
text_index = pc.Index(TEXT_INDEX_NAME)
image_index = pc.Index(IMAGE_INDEX_NAME)

def encode_text(text):
    """Generate OpenAI text embedding"""
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error encoding text: {e}")
        return None

def encode_image(image_path=None, pil_image=None):
    """Generate CLIP embedding for an image"""
    try:
        if image_path:
            image = Image.open(image_path).convert('RGB')
        elif pil_image:
            image = pil_image.convert('RGB')
        else:
            return None
            
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        return image_features.cpu().numpy()[0].tolist()
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def extract_figure_number(filename):
    """Extract figure number from filename like figure-1-1.jpg"""
    figure_match = re.search(r'figure-(\d+)', filename.lower())
    return figure_match.group(1) if figure_match else "unknown"

def index_figures_folder(directory=FIGURES_DIR):
    """Index all images in the figures directory"""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist!")
        return
    
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"Found {len(image_files)} images in {directory}")
    
    vectors = []
    for filename in image_files:
        image_path = os.path.join(directory, filename)
        figure_num = extract_figure_number(filename)
        embedding = encode_image(image_path=image_path)
        
        if embedding:
            vector_id = f"fig_{figure_num}_{uuid.uuid4().hex[:6]}"
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "type": "figure",
                    "filename": filename,
                    "figure_number": figure_num,
                    "filepath": os.path.abspath(image_path)
                }
            })
    
    if vectors:
        image_index.upsert(vectors=vectors, namespace=IMAGE_NAMESPACE)
        print(f"Indexed {len(vectors)} figures")

def index_pdf(pdf_path=PDF_PATH):
    """Extract and index text and images from PDF"""
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
        
    doc = fitz.open(pdf_path)
    print(f"Processing PDF: {pdf_path} with {len(doc)} pages")
    
    for page_num, page in enumerate(doc):
        print(f"Processing page {page_num+1}/{len(doc)}")
        
        # Extract and index text
        text = page.get_text()
        chunks = [text[i:i+1000] for i in range(0, len(text), 900) if text[i:i+1000].strip()]
        
        for chunk_idx, chunk in enumerate(chunks):
            text_embedding = encode_text(chunk)
            if text_embedding:
                vector_id = f"text_p{page_num}_c{chunk_idx}_{uuid.uuid4().hex[:6]}"
                
                text_index.upsert(
                    vectors=[{
                        "id": vector_id,
                        "values": text_embedding,
                        "metadata": {
                            "type": "text",
                            "page": page_num,
                            "content": chunk[:1000]
                        }
                    }],
                    namespace=TEXT_NAMESPACE
                )
        
        # Extract and index images
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                image = Image.open(BytesIO(image_bytes)).convert("RGB")
                image_embedding = encode_image(pil_image=image)
                
                if image_embedding:
                    temp_dir = "temp_images"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, f"page_{page_num}_img_{img_index}.jpg")
                    image.save(temp_path)
                    
                    vector_id = f"img_p{page_num}_i{img_index}_{uuid.uuid4().hex[:6]}"
                    
                    image_index.upsert(
                        vectors=[{
                            "id": vector_id,
                            "values": image_embedding,
                            "metadata": {
                                "type": "pdf_image",
                                "page": page_num,
                                "image_index": img_index,
                                "filepath": os.path.abspath(temp_path)
                            }
                        }],
                        namespace=IMAGE_NAMESPACE
                    )
            except Exception as e:
                print(f"Error processing image {img_index} on page {page_num}: {e}")
    
    doc.close()
    print(f"Finished indexing PDF: {pdf_path}")

def search(query, top_k_text=2, top_k_images=1):
    """Search for both text and images using a text query"""
    # Get text results using text embedding
    text_embedding = encode_text(query)
    text_results = text_index.query(
        vector=text_embedding,
        top_k=top_k_text,
        include_metadata=True,
        namespace=TEXT_NAMESPACE
    )
    
    # Create CLIP embedding to search images
    clip_embedding = model.get_text_features(
        **processor(text=query, return_tensors="pt", truncation=True).to(device)
    ).detach().cpu().numpy()[0].tolist()
    
    # Get only PDF images
    pdf_images = image_index.query(
        vector=clip_embedding,
        top_k=top_k_images,
        include_metadata=True,
        namespace=IMAGE_NAMESPACE,
        filter={"type": {"$eq": "pdf_image"}}
    )
    
    return text_results['matches'], pdf_images['matches']

def display_results(text_results, image_results):
    """Display combined search results"""
    print("\n=== TEXT EXPLANATION ===")
    if not text_results:
        print("No text results found!")
    else:
        print("\nFound text information:")
        for match in text_results:
            metadata = match['metadata']
            print(f"\nPage {metadata.get('page', 'unknown')} (Score: {match['score']:.4f})")
            if 'content' in metadata:
                print(metadata['content'])
    
    print("\n=== RELEVANT IMAGE ===")
    if not image_results:
        print("No image results found!")
    else:
        image = image_results[0]
        metadata = image['metadata']
        filepath = metadata.get('filepath')
        
        if filepath and os.path.exists(filepath):
            print(f"Found relevant image (Score: {image['score']:.4f})")
            print(f"Opening image: {filepath}")
            try:
                if os.name == 'nt':  # Windows
                    os.system(f'start "" "{filepath}"')
                elif os.name == 'posix':  # macOS or Linux
                    if sys.platform == 'darwin':  # macOS
                        os.system(f'open "{filepath}"')
                    else:  # Linux
                        os.system(f'xdg-open "{filepath}"')
            except Exception as e:
                print(f"Failed to open image file: {e}")

def main():
    # Check if indexes have vectors
    text_stats = text_index.describe_index_stats()
    image_stats = image_index.describe_index_stats()
    
    # Get vector counts for each namespace
    text_count = 0
    image_count = 0
    
    if TEXT_NAMESPACE in text_stats.get('namespaces', {}):
        text_count = text_stats['namespaces'][TEXT_NAMESPACE]['vector_count']
    
    if IMAGE_NAMESPACE in image_stats.get('namespaces', {}):
        image_count = image_stats['namespaces'][IMAGE_NAMESPACE]['vector_count']
    
    print(f"Text index: {text_count} vectors, Image index: {image_count} vectors")
    
    # Index data if needed
    if text_count == 0 or image_count == 0:
        print("Indexes are empty. Indexing data...")
        index_figures_folder()
        index_pdf()
    else:
        index_choice = input("Do you want to re-index data? (y/n): ").lower()
        if index_choice == 'y':
            index_figures_folder()
            index_pdf()
    
    # Interactive search loop
    while True:
        query = input("\nEnter your search query (or 'quit' to exit): ")
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
            
        # Perform search
        text_results, image_results = search(query)
        display_results(text_results, image_results)

if __name__ == "__main__":
    main()