import os
import gc
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from llama_index.core import Settings
from llama_index.llms.deepseek import DeepSeek
from llama_index.experimental.query_engine import PandasQueryEngine

# Load environment variables
load_dotenv('.env', override=True)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.dataframes = {}
    st.session_state.query_engines = {}
    st.session_state.current_file = None

def load_llm():
    llm = DeepSeek(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        request_timeout=120.0
    )
    return llm

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def display_dataframe(df, file_name):
    st.markdown(f"### Preview: {file_name}")
    st.dataframe(df)

# Sidebar for file upload
with st.sidebar:
    st.header("Upload your data")
    
    uploaded_file = st.file_uploader("Choose Excel or CSV file", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        try:
            # Read the file into a pandas DataFrame
            if file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(uploaded_file)
            elif file_extension == '.csv':
                df = pd.read_csv(uploaded_file)
            
            # Store the DataFrame in session state
            st.session_state.dataframes[file_name] = df
            st.session_state.current_file = file_name
            
            # Create a PandasQueryEngine for this DataFrame
            llm = load_llm()
            Settings.llm = llm
            
            # Create the query engine with synthesis for better formatted responses
            query_engine = PandasQueryEngine(
                df=df,
                verbose=True,
                synthesize_response=True
            )
            
            # Store the query engine in session state
            st.session_state.query_engines[file_name] = query_engine
            
            st.success(f"File '{file_name}' loaded successfully!")
            
            # Display the DataFrame preview
            display_dataframe(df, file_name)
            
        except Exception as e:
            st.error(f"Error loading file: {e}")

# Main area for chat
col1, col2 = st.columns([6, 1])

with col1:
    current_file = st.session_state.get('current_file', 'No file selected')
    st.header(f"Chat with your data: {current_file}")

with col2:
    st.button("Clear Chat ↺", on_click=reset_chat)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your data..."):
    # Check if a file is loaded
    if not st.session_state.current_file:
        st.warning("Please upload a file first!")
        st.stop()
    
    current_file = st.session_state.current_file
    query_engine = st.session_state.query_engines.get(current_file)
    
    if not query_engine:
        st.warning("No query engine found. Please reload the file.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process query and display response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Execute the query - PandasQueryEngine doesn't support streaming
            response = query_engine.query(prompt)
            
            # If metadata contains a pandas instruction, show it as "executed code"
            if "pandas_instruction_str" in response.metadata:
                code = response.metadata["pandas_instruction_str"]
                with st.expander("View the pandas code that was executed"):
                    st.code(code, language="python")
            
            # Display the response
            message_placeholder.markdown(str(response))
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": str(response)})
            
        except Exception as e:
            st.error(f"Error processing query: {e}")
            error_message = "Sorry, I encountered an error while processing your question."
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})