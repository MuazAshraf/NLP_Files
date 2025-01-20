from flask import Flask, request, jsonify, send_file
from uuid import uuid4
from dotenv import load_dotenv
import os
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Sequence, Literal
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolInvocation
import json
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import FunctionMessage
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import Neo4jVector
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import ElevenLabsText2SpeechTool
import speech_recognition as sr
import whisper
import numpy as np
import tempfile
import wave


# Initialize Flask app
app = Flask(__name__)

# Load environment variables (if any)
from dotenv import load_dotenv
load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')

# Initialize message history
message_history = ChatMessageHistory()

# Initialize recognizer and Whisper model
recognizer = sr.Recognizer()
model = whisper.load_model("medium.en")

# Initialize language model
llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0.2,
    n=1
)
# Initialize Pinecone# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("testing")

# Initialize web search tool
web_search_tool = TavilySearchResults(description="Search the internet for real-time information and current events", k=3)

# Initialize the ElevenLabs TTS tool
tts_tool = ElevenLabsText2SpeechTool()
# Instantiate OpenAI model
openai_chat_model = ChatOpenAI(model="gpt-4o-mini")
# Load and split documents for RAG
file_path = "data/testing2.pdf" 
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=350, chunk_overlap=50)
chunked_documents = text_splitter.split_documents(pages)

# Instantiate the Embedding Model and FAISS index
embeddings = OpenAIEmbeddings()
vector_store = PineconeVectorStore.from_documents(chunked_documents, embedding=embeddings, index_name="testing")

retriever = vector_store.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_documents",
    "Search and return information from the context you have only."
)

# Initialize tools
tools = [retriever_tool, web_search_tool, tts_tool]

# Initialize prompt
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages

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
