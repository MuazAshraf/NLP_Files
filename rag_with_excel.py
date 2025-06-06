import os
import gc
import tempfile
import uuid
import pandas as pd
import hashlib  # For creating unique IDs from file content

from llama_index.core import Settings, StorageContext, load_index_from_storage  # Add these imports
from llama_index.llms.deepseek import DeepSeek
from llama_index.core import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.file import PandasExcelReader
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from dotenv import load_dotenv
import streamlit as st

# Create persistent directories for storage
UPLOAD_DIR = "uploaded_files"
INDEX_DIR = "persisted_indexes"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

load_dotenv('.env', override=True)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

@st.cache_resource
def load_llm():
    llm = DeepSeek(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        request_timeout=120.0
    )
    return llm

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

# Function to create a unique ID from file content
def get_file_hash(file_content):
    return hashlib.md5(file_content).hexdigest()

# Renamed function to handle both Excel and CSV
def display_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension in ['.xlsx', '.xls']:
        st.markdown("### Excel Preview")
        # Read the Excel file
        df = pd.read_excel(file)
    elif file_extension == '.csv':
        st.markdown("### CSV Preview")
        # Read the CSV file
        df = pd.read_csv(file)
    else:
        st.warning(f"Preview not available for {file_extension} files.")
        return
        
    # Display the dataframe
    st.dataframe(df)


with st.sidebar:
    st.header(f"Add your documents!")
    
    uploaded_file = st.file_uploader("Choose your `.xlsx`, `.xls`, or `.csv` file", type=["xlsx", "xls", "csv"])

    if uploaded_file:
        try:
            # Read file content for hashing
            file_content = uploaded_file.getvalue()
            
            # Create a unique ID for this file based on its content
            file_hash = get_file_hash(file_content)
            file_name = uploaded_file.name
            
            # Define paths for persistence
            saved_file_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file_name}")
            index_persist_dir = os.path.join(INDEX_DIR, file_hash)
            
            # Save file permanently if it doesn't exist
            if not os.path.exists(saved_file_path):
                with open(saved_file_path, "wb") as f:
                    f.write(file_content)
                st.sidebar.success(f"File saved permanently as: {file_name}")
                
            # Check if we already have this index persisted
            if os.path.exists(index_persist_dir):
                st.sidebar.info("Found existing index. Loading...")
                # Load the existing index
                storage_context = StorageContext.from_defaults(persist_dir=index_persist_dir)
                index = load_index_from_storage(storage_context)
                
                # Get LLM
                llm = load_llm()
                Settings.llm = llm
                
                # Create query engine
                query_engine = index.as_query_engine(
                    streaming=True,
                    similarity_top_k=3,
                    node_postprocessors=[]
                )
                
                # Set up the custom prompt template
                qa_prompt_tmpl_str = (
                    "Context information is below.\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Given the context information above I want you to think step by step to answer the query in a highly precise and crisp manner focused on the final answer, incase case you don't know the answer say 'I don't know!'.\n"
                    "Query: {query_str}\n"
                    "Answer: "
                )
                qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
                query_engine.update_prompts(
                    {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                )
                
                st.session_state.file_cache[file_name] = query_engine
                st.sidebar.success("Index loaded successfully!")
                
            else:
                # Index doesn't exist, create it
                st.sidebar.info("Creating new index...")
                
                # Create a temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_file_path = os.path.join(temp_dir, file_name)
                    
                    # Write the file to the temp directory for processing
                    with open(temp_file_path, "wb") as f:
                        f.write(file_content)
                    
                    # Create the appropriate reader based on file extension
                    file_extension = os.path.splitext(file_name)[1].lower()
                    
                    if file_extension in ['.xlsx', '.xls']:
                        excel_reader = PandasExcelReader()
                        loader = SimpleDirectoryReader(
                            input_dir=temp_dir,
                            file_extractor={".xlsx": excel_reader, ".xls": excel_reader},
                        )
                    else:
                        # For CSV and other files, use default reader
                        loader = SimpleDirectoryReader(
                            input_dir=temp_dir,
                        )
                    
                    docs = loader.load_data()
                    
                    # Check for empty documents
                    if not docs:
                        st.error(f"Failed to extract content from {file_name}. Please check the file format.")
                        st.stop()

                    # Setup LLM & embedding model
                    llm = load_llm()
                    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5", trust_remote_code=True)
        
                    
                    # Configure settings
                    Settings.embed_model = embed_model
                    Settings.llm = llm
                    
                    # Create storage context for persistence
                    storage_context = StorageContext.from_defaults()
                    
                    # Create the index
                    node_parser = SentenceSplitter(
                        chunk_size=512,
                        chunk_overlap=50
                    )
                    index = VectorStoreIndex.from_documents(
                        documents=docs, 
                        transformations=[node_parser], 
                        storage_context=storage_context,
                        show_progress=True
                    )
                    
                    # Persist the index to disk
                    index.storage_context.persist(persist_dir=index_persist_dir)
                    st.sidebar.success(f"Index created and saved to disk!")

                    # Create the query engine
                    query_engine = index.as_query_engine(
                        streaming=True,
                        similarity_top_k=3,
                        node_postprocessors=[]
                    )

                    # Set up custom prompt template
                    qa_prompt_tmpl_str = (
                        "Context information is below.\n"
                        "---------------------\n"
                        "{context_str}\n"
                        "---------------------\n"
                        "Given the context information above I want you to think step by step to answer the query in a highly precise and crisp manner focused on the final answer, incase case you don't know the answer say 'I don't know!'.\n"
                        "Query: {query_str}\n"
                        "Answer: "
                    )
                    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
                    query_engine.update_prompts(
                        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                    )
                    
                    # Cache the query engine
                    st.session_state.file_cache[file_name] = query_engine
            
            # Store the current file name for the chat interface
            st.session_state.current_file = file_name
            
            # Inform the user that everything is ready
            st.success(f"Ready to chat with: {file_name}")
            display_file(uploaded_file)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.error(traceback.format_exc())
            st.stop()

col1, col2 = st.columns([6, 1])

with col1:
    # Show which file we're currently chatting with
    current_file = st.session_state.get('current_file', 'No file selected')
    st.header(f"RAG over Excel/CSV: {current_file}")

with col2:
    st.button("Clear Chat ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about your document..."):
    # Check if we have a file loaded
    if 'current_file' not in st.session_state:
        st.warning("Please upload a file first!")
        st.stop()
        
    query_engine = st.session_state.file_cache.get(st.session_state.current_file)
    if not query_engine:
        st.warning("No query engine found for the current file. Please reload the file.")
        st.stop()
        
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Process the query
            streaming_response = query_engine.query(prompt)
            
            for chunk in streaming_response.response_gen:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error processing query: {e}")
            full_response = "Sorry, I encountered an error while processing your question."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})