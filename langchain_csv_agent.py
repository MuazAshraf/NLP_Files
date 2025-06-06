from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv('.env', override=True)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Load data explicitly with pandas first (good practice)
# Add file path as a variable so we can examine it
file_path = "Passenger.csv"

# Simple if/else to handle different file types
if file_path.endswith('.csv'):
    df = pd.read_csv(file_path)
elif file_path.endswith(('.xls', '.xlsx')):
    df = pd.read_excel(file_path)
else:
    raise ValueError(f"Unsupported file format: {file_path}. Please use CSV or Excel files.")

# Create the agent with the security parameter
agent = create_pandas_dataframe_agent(
    ChatDeepSeek(temperature=0, model="deepseek-chat", api_key=DEEPSEEK_API_KEY),
    df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True
)

# Now your query will work
result = agent.invoke("give me the full details on NASSER FALEH ALTAMER.")
print(result)