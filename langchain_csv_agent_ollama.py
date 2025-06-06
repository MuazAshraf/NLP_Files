import streamlit as st
import pandas as pd
import os
from langchain.agents.agent_types import AgentType
from langchain_ollama import OllamaLLM
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


# Set up page
st.set_page_config(page_title="Chat with your Excel/CSV")
st.title("Chat with your Excel/CSV file")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None
    
if "agent" not in st.session_state:
    st.session_state.agent = None

# Clear chat history
def reset_chat():
    st.session_state.messages = []

# Sidebar for file upload
with st.sidebar:
    st.header("Upload your file")
    
    uploaded_file = st.file_uploader("Choose Excel or CSV file", type=["xlsx", "xls", "csv"])
    
    if uploaded_file:
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()
        
        try:
            # Read the file based on its extension
            if file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(uploaded_file)
            elif file_extension == '.csv':
                df = pd.read_csv(uploaded_file)
            
            # Save the dataframe to session state
            st.session_state.df = df
            
            # Example prefix with stricter formatting instructions
            AGENT_PREFIX = """
            You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
            You have a tool named `python_repl_ast` for executing python commands on the dataframe.
            Respond with a Thought, then Action, then Action Input.
            Your final response MUST be ONLY in the format:

            Thought: [Your reasoning]
            Action: python_repl_ast
            Action Input: [Valid python code to execute]

            NEVER include any other text before "Thought:" or between "Action:" and "Action Input:".
            If you have the final answer, use the format:

            Thought: [Your reasoning]
            Final Answer: [The final answer to the original input question]

            Begin!
            """

            # Create the agent
            agent = create_pandas_dataframe_agent(
                OllamaLLM(model="llama3.1:8b"),
                df,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                allow_dangerous_code=True,
                agent_executor_kwargs={"handle_parsing_errors": True},
                prefix=AGENT_PREFIX
            )
            
            # Save the agent to session state
            st.session_state.agent = agent
            
            st.success(f"File loaded: {file_name}")
            
            # Display dataframe preview in sidebar
            st.markdown("### File Preview")
            st.dataframe(df, height=300)
        
        except Exception as e:
            st.error(f"Error: {e}")

# Main chat area
# Clear chat button
col1, col2 = st.columns([6, 1])
with col2:
    st.button("Clear Chat", on_click=reset_chat)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if st.session_state.df is not None:
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        if st.session_state.agent:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                try:
                    with st.spinner("Thinking..."):
                        result = st.session_state.agent.invoke(prompt)
                        response_text = result.get("output", str(result))
                    
                    # Display the response
                    message_placeholder.markdown(response_text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    error_message = f"Error processing your question: {str(e)}"
                    message_placeholder.markdown(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
else:
    st.info("Please upload an Excel or CSV file to begin.")