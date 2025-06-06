#STEP 1
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

#STEP 2
# Initialize Flask app
app = Flask(__name__)

# Load environment variables (if any)
from dotenv import load_dotenv
load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')

# Initialize message history
message_history = ChatMessageHistory()


# Initialize language model
llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0.8,
    n=1
)
# Initialize Pinecone# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("testing")

# Initialize web search tool
web_search_tool = TavilySearchResults(description="Search the internet for real-time information and current events", k=3)


# Load and split documents for RAG
# file_path = "data/testing2.pdf" 
# loader = PyPDFLoader(file_path)
# pages = loader.load_and_split()
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=350, chunk_overlap=50)
# chunked_documents = text_splitter.split_documents(pages)

# Instantiate the Embedding Model and Pinecone index
embeddings = OpenAIEmbeddings()
vector_store = PineconeVectorStore.from_existing_index(embedding=embeddings, index_name="testing", namespace="certification")

retriever = vector_store.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_documents",
    "Search and return information from the context you have only."
)

# Initialize tools
tools = [retriever_tool, web_search_tool]

# Initialize prompt
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages

#STEP 3

# Initialize agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Initialize agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Initialize agent with chat history
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: message_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

#Step 4
@app.route('/ask', methods=['POST'])
def index():
    try:
        data = request.get_json()
        # Handle nested message format
        question = data['messages'][0]['question'] if 'messages' in data else data['question']
        
        # Get the agent's response
        response = agent_with_chat_history.invoke(
            {"input": question},
            config={"configurable": {"session_id": "x123"}},
        )
        
        # Extract the relevant content from the response
        if isinstance(response, dict):
            response_content = response.get('output') or response.get('response') or str(response)
        else:
            response_content = str(response)
        
        # Return the formatted response
        return jsonify({
            "response": response_content,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500



if __name__ == '__main__':
    app.run(debug=True)

