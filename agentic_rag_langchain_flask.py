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
import tempfile
import wave
from pydub import AudioSegment
import io

# Initialize Flask app
app = Flask(__name__)
message_history = ChatMessageHistory()
MODEL = 'gpt-4o-mini'

llm = ChatOpenAI(
        model=MODEL,
        temperature=0.2,
        n=1
    )
# Load environment variables (if any)
from dotenv import load_dotenv
load_dotenv('.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("testing")
web_search_tool = TavilySearchResults(description="Search the internet for real-time information and current events",k=3)
# Instantiate OpenAI model
openai_chat_model = ChatOpenAI(model="gpt-4o-mini")
# Initialize variables
# neo4j_url = "neo4j+s://cd1f8ccd.databases.neo4j.io"
# neo4j_username = "neo4j"
# neo4j_password = "rLluiIywWddTjCdxCY65SQoPtAwASoUMj_bIJrxLRag"
# graph = None

# # Set Neo4j connection details directly in the code
# graph = Neo4jGraph(
#     url=neo4j_url, 
#     username=neo4j_username, 
#     password=neo4j_password
# )
# cypher = """
#                   MATCH (n)
#                   DETACH DELETE n;
#                 """
# graph.query(cypher)
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
# Define allowed nodes and relationships
# allowed_nodes = [
#     "Tool", 
#     "Route", 
#     "Service", 
#     "API", 
#     "Process", 
#     "File", 
#     "Model", 
#     "Task", 
#     "User"
# ]

# allowed_relationships = [
#     "USES",            # Tool -> Service
#     "CONTAINS",        # Tool -> Route
#     "GENERATES",       # Process -> File
#     "CALLS",           # Route -> API
#     "PROCESSES",       # Process -> Task
#     "DEPENDS_ON",      # Tool -> Model
#     "CREATES",         # User -> Task
#     "INTERACTS_WITH",  # User -> Tool
#     "RELIES_ON"        # API -> Service
# ]


# # Transform documents into graph documents
# transformer = LLMGraphTransformer(
#     llm=openai_chat_model,
#     allowed_nodes=allowed_nodes,
#     allowed_relationships=allowed_relationships,
#     node_properties=True, 
#     relationship_properties=True
# ) 

# graph_documents = transformer.convert_to_graph_documents(pages)
# graph.add_graph_documents(graph_documents, include_source=True)

# # Use the stored connection parameters
# index = Neo4jVector.from_existing_graph(
#     embedding=embeddings,
#     url=neo4j_url,
#     username=neo4j_username,
#     password=neo4j_password,
#     database="neo4j",
#     node_label="Tools",  # Adjust node_label as needed
#     text_node_properties=["id", "text"], 
#     embedding_node_property="embedding", 
#     index_name="vector_index", 
#     keyword_index_name="entity_index", 
#     search_type="hybrid" 
# )
# # Retrieve the graph schema
# schema = graph.get_schema

# # Set up the QA chain
# template = """
# Task: Generate a Cypher statement to query the graph database.

# Instructions:
# Use only relationship types and properties provided in schema.
# Do not use other relationship types or properties that are not provided.

# schema:
# {schema}

# Note: Do not include explanations or apologies in your answers.
# Do not answer questions that ask anything other than creating Cypher statements.
# Do not include any text other than generated Cypher statements.

# Question: {question}""" 

# question_prompt = PromptTemplate(
#     template=template, 
#     input_variables=["schema", "question"] 
# )

# qa = GraphCypherQAChain.from_llm(
#     llm=openai_chat_model,
#     graph=graph,
#     cypher_prompt=question_prompt,
#     verbose=True,
#     allow_dangerous_requests=True
# )

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_documents",
    "Search and return information from the context you have only."
)

tools = [retriever_tool, web_search_tool]
prompt = hub.pull("hwchase17/openai-functions-agent")
prompt.messages
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
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
        # The response might be in different formats depending on the agent's output
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
