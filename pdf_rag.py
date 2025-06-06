from crewai_tools import PDFSearchTool
import re

def clean_text(text):
    """Clean the extracted text by removing extra spaces and fixing formatting"""
    # Remove spaces between single characters
    text = re.sub(r'(?<=\w)\s(?=\w)', '', text)
    # Fix multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Fix line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# Initialize the tool
pdf_path = r'C:\Users\MUAZ\Downloads\MojoSolo-Muaz Verification letter.pdf'
tool = PDFSearchTool(pdf=pdf_path)

# Search with a more specific query
queries = [
    "What is Muaz's job title and role at MojoSolo?",
    "What are Muaz's key responsibilities?",
    "What are the working hours mentioned in the letter?"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = tool.run(query=query)
    cleaned_result = clean_text(result)
    print(f"Answer: {cleaned_result}") 