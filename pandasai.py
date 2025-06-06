import os
import pandas as pd
import pandasai as pai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
PAI_API_KEY = os.getenv("PAI_API_KEY")

# Set API key for PandaAI
pai.api_key.set(PAI_API_KEY)

def chat_with_data(file_path):
    # Determine file type and load data
    if file_path.endswith(('.xlsx', '.xls')):
        # For Excel files
        print(f"Loading Excel file: {file_path}")
        df = pai.read_excel(file_path)
    elif file_path.endswith('.csv'):
        # For CSV files
        print(f"Loading CSV file: {file_path}")
        df = pai.read_csv(file_path)
    else:
        print("Unsupported file format. Please use Excel or CSV files.")
        return

    print("\nFile loaded successfully! Preview:")
    print(df.head())
    
    # Chat loop
    print("\n--- Start chatting with your data (type 'exit' to quit) ---")
    while True:
        user_input = input("\nAsk a question about your data: ")
        
        if user_input.lower() in ('exit', 'quit', 'q'):
            print("Goodbye!")
            break
            
        try:
            # Process the query with PandaAI
            response = df.chat(user_input)
            print("\nAnswer:")
            print(response)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Get file path from user
    file_path = input("Enter the path to your Excel or CSV file: ")
    
    if os.path.exists(file_path):
        chat_with_data(file_path)
    else:
        print(f"File not found: {file_path}")