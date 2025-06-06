from flask import Flask
from dotenv import load_dotenv
import os
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.documents import Document
from IPython.display import display, Markdown

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
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("testing")
web_search_tool = TavilySearchResults(description="Search the internet for real-time information and current events",k=3)

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



tools = [retriever_tool, web_search_tool]

class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]

def grade_documents(state) -> Literal["generate", "web_search"]:
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (messages): The current state

    Returns:
        str: A decision for whether the documents are relevant or not
    """

    print("---CHECK RELEVANCE---")

    # Data model
    class grade(BaseModel):
        """Binary score for relevance check."""

        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    # LLM
    model =  ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)

    # LLM with tool and validation
    llm_with_tool = model.with_structured_output(grade)

    # Prompt
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document to a user question. \n
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.""",
        input_variables=["context", "question"],
    )

    # Chain
    chain = prompt | llm_with_tool

    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    docs = last_message.content

    scored_result = chain.invoke({"question": question, "context": docs})

    score = scored_result.binary_score

    if score == "yes":
        print("---DECISION: DOCS RELEVANT---")
        return "generate"

    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        print(score)
        return "web_search"


### Nodes

def web_search_agent(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["messages"]
    query = question[0].content
    print(question)
    # Web search
    docs = web_search_tool.invoke({"query": query})
    web_results = "\n".join([d["content"] for d in docs])
    web = Document(page_content=web_results)

    # We return a list, because this will get added to the existing list
    return {"messages": [web_results]}

def retrieve_agent(state):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply end.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    model =  ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)
    model = model.bind_tools(tools)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


def rewrite(state):
    """
    Transform the query to produce a better question.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with re-phrased question
    """

    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content

    msg = [
        HumanMessage(
            content=f""" \n
    Look at the input and try to reason about the underlying semantic intent / meaning. \n
    Here is the initial question:
    \n ------- \n
    {question}
    \n ------- \n
    Formulate an improved question: """,
        )
    ]

    llm =  ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)
    response = llm.invoke(msg)
    return {"messages": [response]}


def generate(state):
    """
    Generate answer

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with re-phrased question
    """
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]

    docs = last_message.content

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")

    # LLM
    llm =  ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=OPENAI_API_KEY)

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | llm | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response]}


print("*" * 20 + "Prompt[rlm/rag-prompt]" + "*" * 20)
prompt = hub.pull("rlm/rag-prompt").pretty_print()

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes we will cycle between
workflow.add_node("web_search", web_search_agent)  # web search
workflow.add_node("agent", retrieve_agent)  # agent
retrieve = ToolNode([retriever_tool, web_search_tool])
workflow.add_node("retrieve", retrieve)
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents are relevant
# Call agent node to decide to retrieve or not
workflow.add_edge(START, "agent")

workflow.add_edge("web_search", "generate")

# Decide whether to retrieve
workflow.add_conditional_edges(
    "agent",
    # Assess agent decision
    tools_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "tools": "retrieve",
        END: END,
    },
)

# Edges taken after the `action` node is called.
workflow.add_conditional_edges(
    "retrieve",
    # Assess agent decision
    grade_documents,
)
workflow.add_edge("generate", END)
mermaid_syntax = workflow.draw_mermaid()
checkpointer = MemorySaver()
# Compile
graph = workflow.compile(checkpointer=checkpointer)

# Save to a .mmd file
with open("rag.mmd", "w") as f:
    f.write(mermaid_syntax)

print("Mermaid diagram saved to rag.mmd")

import pprint

inputs = {
    "messages": [
        ("user", "explain the latest development of AI in 2025"),
    ]
}
for output in graph.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Output from node '{key}':")
        pprint.pprint("---")
        pprint.pprint(value, indent=2, width=80, depth=None)
    pprint.pprint("\n---\n")
