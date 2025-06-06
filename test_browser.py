from text_webBrowser.text_web_browser import SimpleTextBrowser, SearchInformationTool

# Initialize browser with downloads folder
browser = SimpleTextBrowser(
    downloads_folder="./downloads",
    serpapi_key="YOUR_SERPAPI_KEY"  # You'll need this for Google search functionality
)

# Create search tool
search_tool = SearchInformationTool(browser)

# Test the browser
result = search_tool.forward("Python programming language")
print(result) 