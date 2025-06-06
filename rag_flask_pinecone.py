from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain import hub
from pinecone import Pinecone, NotFoundException
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os, uuid
from dotenv import load_dotenv
load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
index = pc.Index("testing")

# Define a global variable to store the current namespace
current_namespace = "default_namespace"

def get_all_namespaces():
    """Get all existing namespaces from Pinecone index"""
    try:
        stats = index.describe_index_stats()
        return list(stats.namespaces.keys())
    except Exception as e:
        return []

@app.route('/namespaces', methods=['GET'])
def list_namespaces():
    """Get all available namespaces"""
    namespaces = get_all_namespaces()
    return jsonify({"namespaces": namespaces}), 200

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/documents', methods=['POST'])
def upload_document():
    try:
        namespace = request.form.get('namespace')
        create_new = request.form.get('create_new', 'false').lower() == 'true'
        
        if not namespace:
            return jsonify({"error": "Namespace is required"}), 400
            
        if not create_new and namespace not in get_all_namespaces():
            return jsonify({"error": "Namespace does not exist"}), 400
        
        vector_store = PineconeVectorStore(embedding=embeddings, index=index, namespace=namespace)
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store original filename without extension as title
            doc_title = os.path.splitext(filename)[0]
            
            # Load document based on file type
            extension = filename.rsplit('.', 1)[1].lower()
            if extension == 'pdf':
                loader = PyPDFLoader(filepath)
            elif extension == 'txt':
                loader = TextLoader(filepath)
                
            docs = loader.load()
            
            # Split and index documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)
            
            # Add unique IDs and document title to metadata
            chunks_metadata = []
            for split in splits:
                chunk_id = str(uuid.uuid4())
                split.metadata.update({
                    'doc_id': chunk_id,
                    'doc_title': doc_title,
                    'original_filename': filename,
                    'chunk_index': len(chunks_metadata) + 1,
                    'total_chunks': len(splits)
                })
                chunks_metadata.append({
                    'id': chunk_id,
                    'title': doc_title,
                    'chunk_index': split.metadata['chunk_index']
                })
            
            if not splits:
                return jsonify({"error": "Document contains no text to embed."}), 400

            vector_store.add_documents(splits)

    finally:
        os.remove(filepath)  # Clean up uploaded file
        
        return jsonify({
            "message": f"Successfully uploaded and indexed {len(splits)} chunks",
            "document_title": doc_title,
            "filename": filename,
            "total_chunks": len(splits),
            "chunks": chunks_metadata
        }), 201

@app.route('/namespace', methods=['PUT'])
def update_namespace():
    """Update namespace name"""
    data = request.json
    old_namespace = data.get('old_namespace')
    new_namespace = data.get('new_namespace')
    
    if not old_namespace or not new_namespace:
        return jsonify({"error": "Both old and new namespace names are required"}), 400
        
    if old_namespace not in get_all_namespaces():
        return jsonify({"error": "Original namespace does not exist"}), 404
        
    try:
        # Get all vectors from old namespace
        vector_store = PineconeVectorStore.from_existing_index(
            embedding=embeddings, 
            index_name="testing", 
            namespace=old_namespace
        )
        
        # Fetch all vectors (you might want to do this in batches for large datasets)
        results = index.query(
            namespace=old_namespace,
            vector=[0]*1536,  # dummy vector
            top_k=10000,
            include_metadata=True,
            include_values=True
        )
        
        if results.matches:
            # Create new namespace with existing vectors
            index.upsert(
                vectors=[(m.id, m.values, m.metadata) for m in results.matches],
                namespace=new_namespace
            )
            
            # Delete old namespace
            index.delete(delete_all=True, namespace=old_namespace)
            
        return jsonify({"message": f"Namespace updated from {old_namespace} to {new_namespace}"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update namespace: {str(e)}"}), 500

@app.route('/namespace/<namespace>', methods=['DELETE'])
def delete_namespace(namespace):
    """Delete an entire namespace"""
    if namespace not in get_all_namespaces():
        return jsonify({"error": f"Namespace '{namespace}' does not exist"}), 404
    
    try:
        index.delete(delete_all=True, namespace=namespace)
        return jsonify({"message": f"Namespace '{namespace}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/namespace/<namespace>/documents', methods=['DELETE'])
def delete_all_documents(namespace):
    """Delete all documents in a namespace but keep the namespace"""
    if namespace not in get_all_namespaces():
        return jsonify({"error": f"Namespace '{namespace}' does not exist"}), 404
    
    try:
        index.delete(delete_all=True, namespace=namespace)
        return jsonify({"message": f"All documents in namespace '{namespace}' deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/namespace/<namespace>/document', methods=['DELETE'])
def delete_document(namespace):
    """Delete a specific document by ID or title"""
    if namespace not in get_all_namespaces():
        return jsonify({"error": f"Namespace '{namespace}' does not exist"}), 404
    
    data = request.json
    doc_id = data.get("doc_id")
    doc_title = data.get("doc_title")
    
    if not doc_id and not doc_title:
        return jsonify({"error": "Either doc_id or doc_title is required"}), 400
    
    try:
        if doc_id:
            # Delete by ID
            index.delete(ids=[doc_id], namespace=namespace)
            return jsonify({"message": f"Document with ID '{doc_id}' deleted from namespace '{namespace}'"}), 200
        
        elif doc_title:
            # Delete by title - first find all chunks with this title
            results = index.query(
                namespace=namespace,
                vector=[0]*1536,  # dummy vector
                top_k=10000,
                include_metadata=True
            )
            
            # Filter matches by document title
            doc_ids = [
                match.id for match in results.matches 
                if match.metadata.get('doc_title') == doc_title
            ]
            
            if not doc_ids:
                return jsonify({"error": f"No document with title '{doc_title}' found in namespace '{namespace}'"}), 404
            
            # Delete all chunks of this document
            index.delete(ids=doc_ids, namespace=namespace)
            return jsonify({
                "message": f"Document '{doc_title}' deleted from namespace '{namespace}'",
                "chunks_deleted": len(doc_ids)
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")
graph_builder = StateGraph(MessagesState)

@tool(response_format="content_and_artifact")
def retrieve(query: str, namespace: str = None):
    """Retrieve information related to a query."""
    # Use the global namespace if none is provided
    search_namespace = namespace if namespace else current_namespace
    
    vector_store = PineconeVectorStore.from_existing_index(
        embedding=embeddings, index_name="testing", namespace=search_namespace
    )
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])


# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}

def reflect(state: MessagesState):
    """Reflect on and critique the generated answer."""
    # Get the last AI message
    for message in reversed(state["messages"]):
        if message.type == "ai" and not message.tool_calls:
            last_response = message.content
            break
    
    reflection_prompt = f"""
    You are a critical reviewer. Review the following response to a user query.
    Identify any inaccuracies, missing information, or areas for improvement.
    
    User query: {state["messages"][0].content}
    Response: {last_response}
    
    Provide specific suggestions for improvement:
    """
    
    reflection = llm.invoke(reflection_prompt)
    return {"messages": [SystemMessage(content=f"Reflection: {reflection.content}")]}

def improve(state: MessagesState):
    """Improve the response based on reflection."""
    # Get original query and reflection
    original_query = None
    reflection = None
    
    for message in state["messages"]:
        if message.type == "human":
            original_query = message.content
        elif message.type == "system" and "Reflection:" in message.content:
            reflection = message.content
    
    improvement_prompt = f"""
    Based on the following reflection, improve your response to the user's query.
    
    User query: {original_query}
    {reflection}
    
    Improved response:
    """
    
    improved_response = llm.invoke(improvement_prompt)
    return {"messages": [improved_response]}

memory = MemorySaver()
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)
graph_builder.add_node("reflect", reflect)
graph_builder.add_node("improve", improve)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", "reflect")
graph_builder.add_edge("reflect", "improve")
graph_builder.add_edge("improve", END)

graph = graph_builder.compile(checkpointer=memory)

# Replace the diagram generation code with this error-handled version
try:
    # Save the graph visualization as a PNG file with increased timeout
    graph_png = graph.get_graph().draw_mermaid_png()
    with open('rag_flow_diagram.png', 'wb') as f:
        f.write(graph_png)
    
    # Add a route to serve the diagram
    @app.route('/flow-diagram')
    def show_diagram():
        return send_file('rag_flow_diagram.png', mimetype='image/png')
except Exception as e:
    print(f"Warning: Could not generate flow diagram: {str(e)}")
    # Create a simple placeholder route
    @app.route('/flow-diagram')
    def show_diagram():
        return jsonify({"error": "Flow diagram generation failed. The service is still functional."}), 503

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    input_message = data.get("message", "")
    namespace = data.get("namespace", "default_namespace")
    thread_id = data.get("thread_id", str(uuid.uuid4())) 
    
    # Validate namespace exists
    if namespace not in get_all_namespaces():
        return jsonify({"error": f"Namespace '{namespace}' does not exist"}), 404
    
    # Set the global namespace for this request
    global current_namespace
    current_namespace = namespace
    
    config = {"configurable": {"thread_id": thread_id}}
    response_messages = []
    
    for step in graph.stream(
        {"messages": [{"role": "user", "content": input_message}]},
        stream_mode="values",
        config=config,
    ):
        if step["messages"][-1].type == "ai" and not step["messages"][-1].tool_calls:
            response_messages.append(step["messages"][-1].content)

    # Get the final response
    final_response = response_messages[-1] if response_messages else "No response generated"

    return jsonify({
        "response": final_response,
        "thread_id": thread_id,
        "namespace": namespace,
        "query": input_message
    }), 200

# Add a new endpoint to list documents by title in a namespace
@app.route('/namespace/<namespace>/documents', methods=['GET'])
def list_documents(namespace):
    """List all documents in a namespace grouped by title"""
    if namespace not in get_all_namespaces():
        return jsonify({"error": f"Namespace '{namespace}' does not exist"}), 404
    
    try:
        # Query with dummy vector to get metadata
        results = index.query(
            namespace=namespace,
            vector=[0]*1536,  # dummy vector
            top_k=10000,
            include_metadata=True
        )
        
        # Group chunks by document title
        documents = {}
        for match in results.matches:
            title = match.metadata.get('doc_title')
            if not title:
                continue
                
            if title not in documents:
                documents[title] = {
                    'title': title,
                    'filename': match.metadata.get('original_filename'),
                    'total_chunks': match.metadata.get('total_chunks'),
                    'chunks': []
                }
            documents[title]['chunks'].append({
                'id': match.id,
                'chunk_index': match.metadata.get('chunk_index')
            })
            
        return jsonify({
            "namespace": namespace,
            "document_count": len(documents),
            "documents": list(documents.values())
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

