#-----------------------------Part 1 - Initial Setup and Imports:-----------------------------
import openai
from flask import Flask, request, jsonify
import re, time, os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import tiktoken
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import tempfile, requests
from openai import OpenAI

import instructor
from pydantic import BaseModel, Field, create_model
from typing import List, Optional, Dict, Any, Type, get_type_hints, Union

# Load environment variables
load_dotenv('.env')
app = Flask(__name__)
# Initialize OpenAI client with LangSmith wrapper and instructor
client = wrap_openai(openai.Client())
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
instructor_client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

# Constants
GPT_MODEL = "gpt-4o-mini"
max_token = 100000
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
# Special instruction for the agent
SPECIAL_INSTRUCTION = """
This is a general-purpose scraper that can extract information from any website, document, 
image, or PDF. Make sure to extract all relevant information from any available source, 
including embedded documents and images that might contain important details.
"""

#-----------------------------Part 2 - Define Pydantic Models:-----------------------------
# Define the core data structure for information extraction
class DataPoints(BaseModel):
    """Generic data structure for any website/document"""
    title: str = Field(..., description="The main title or name")
    description: Optional[str] = Field(None, description="Comprehensive description or overview")
    key_points: List[str] = Field([], description="Important points and facts")
    contact: Optional[Dict[str, Any]] = Field({}, description="Contact information including email, phone, address, contact forms")
    location: Optional[Dict[str, Any]] = Field({}, description="Physical location details including address, city, country, zip code")
    social_media: Optional[Dict[str, str]] = Field({}, description="Social media links including LinkedIn, Twitter, Facebook, Instagram, etc.")
    services: Optional[List[str]] = Field([], description="List of services or products offered")
    team: Optional[List[Dict[str, Any]]] = Field([], description="Team members or key personnel information")
    company_info: Optional[Dict[str, Any]] = Field({}, description="Company information including founding date, size, industry")
    technologies: Optional[List[str]] = Field([], description="Technologies, tools, or platforms used/mentioned")
    certifications: Optional[List[str]] = Field([], description="Certifications, awards, or recognitions")
    partnerships: Optional[List[str]] = Field([], description="Partner companies or organizations")
    resources: Optional[Dict[str, Any]] = Field({}, description="Available resources like documents, downloads, guides")
    metadata: Dict[str, Any] = Field({}, description="Any additional structured information")


#----------------------------Part 3 - Helper Functions:-----------------------------
# Helper functions for data processing and file handling
def filter_empty_fields(model_instance: BaseModel) -> dict:
    """
    Recursively filter out empty fields from a Pydantic model instance.
    
    Args:
    model_instance (BaseModel): The Pydantic model instance to filter.
    
    Returns:
    dict: A dictionary with non-empty fields and their types.
    """
    def _filter(data: Any, field_type: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: _filter(v, field_type.get(k, type(v)) if isinstance(field_type, dict) else type(v))
                for k, v in data.items()
                if v not in [None, "", [], {}, "null", "None"]
            }
        elif isinstance(data, list):
            return [
                _filter(item, field_type.__args__[0] if hasattr(field_type, '__args__') else type(item))
                for item in data
                if item not in [None, "", [], {}, "null", "None"]
            ]
        else:
            return data

    data_dict = model_instance.dict(exclude_none=True)
    print(f"Data dict: {data_dict}")
    field_types = get_type_hints(model_instance.__class__)
    print(f"Field types: {field_types}")

    def get_inner_type(field_type):
        if hasattr(field_type, '__origin__') and field_type.__origin__ == list:
            return list
        return field_type

    filtered_dict = {
        k: {
            "value": _filter(v, get_inner_type(field_types.get(k, type(v)))),
            "type": str(get_inner_type(field_types.get(k, type(v))).__name__)
        }
        for k, v in data_dict.items()
        if v not in [None, "", [], {}, "null", "None"]
    }
    print(f"Filtered dict: {filtered_dict}")

    return filtered_dict

def create_filtered_model(data: List[Dict[str, Any]], base_model: Type[BaseModel], links_scraped: List[str]) -> Type[BaseModel]:
    """
    Create a filtered Pydantic model based on the provided data and base model.
    
    Args:
    data (List[Dict[str, Any]]): List of dictionaries containing field information.
    base_model (Type[BaseModel]): The base Pydantic model to extend from.
    links_scraped (List[str]): List of already scraped links.
    
    Returns:
    Type[BaseModel]: A new Pydantic model with filtered fields.
    """
    # Filter fields where value is None
    filtered_fields = {item['name']: item['value'] for item in data if item['value'] is None or isinstance(item['value'], list)}

    # Get fields with their annotations and descriptions
    fields_with_descriptions = {
        field: (base_model.__annotations__[field], Field(..., description=base_model.__fields__[field].description))
        for field in filtered_fields
    }
    
    # Constructing the desired JSON output
    data_to_collect = [
        {"name": field_name, "description": field_info.description}
        for field_name, (field_type, field_info) in fields_with_descriptions.items()
    ]

    print(f"Fields with descriptions: {data_to_collect}")
    # Create and return new Pydantic model
    FilteredModel = create_model('FilteredModel', **fields_with_descriptions)

    ExtendedDataPoints = create_model(
        'DataPoints',
        relevant_urls_might_contain_further_info=(List[str], Field([], description=f"{SPECIAL_INSTRUCTION} Relevant urls that we should scrape further that might contain information related to data points that we want to find; [DATA POINTS] {data_to_collect} [/END DATA POINTS] Prioritise urls on official their own domain first, even file url of image or pdf - those links can often contain useful information, we should always prioritise those urls instead of external ones; return None if cant find any; links cannot be any of the following: {links_scraped}")),
        __base__=FilteredModel
    )

    return ExtendedDataPoints
#---------------------------------Part 4 - File Processing Functions:---------------------------------
# Llama parser functions

def download_file(url):
    """
    Download a file from a given URL and save it temporarily.
    
    Args:
    url (str): The URL of the file to download.
    
    Returns:
    str: The path to the temporarily saved file.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_extension = os.path.splitext(url)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"Failed to download file: {response}")

def create_parse_job(file_url):
    """
    Create a parsing job for a given file URL using the Llama API.
    
    Args:
    file_url (str): The URL of the file to parse.
    
    Returns:
    str: The job ID of the created parsing job.
    """
    file_path = download_file(file_url)

    upload_url = "https://api.cloud.llamaindex.ai/api/parsing/upload"
    language = ["en"]
    parsing_instruction = "your_parsing_instruction"

    files = {"file": open(file_path, "rb")}

    data = {"language": language, "parsing_instruction": parsing_instruction}

    headers = {"Accept": "application/json", "Authorization": f"Bearer {LLAMA_API_KEY}"}

    response = requests.post(upload_url, files=files, data=data, headers=headers)

    # Clean up the temporary file
    os.remove(file_path)

    return response.json().get("id")

def get_content(job_id):
    """
    Retrieve the parsed content for a given job ID from the Llama API.
    
    Args:
    job_id (str): The ID of the parsing job.
    
    Returns:
    str: The parsed markdown content or an error message.
    """
    url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {LLAMA_API_KEY}"}

    result = requests.get(url, headers=headers)

    try:
        if result.status_code == 200:
            return result.json().get("markdown")
        else:
            return f"Failed to get content: {result.status_code}"
    except Exception as e:
        return f"Failed to get content: {e}"

def check_status(job_id):
    """
    Check the status of a parsing job using the Llama API.
    
    Args:
    job_id (str): The ID of the parsing job.
    
    Returns:
    str: The status of the job or an error message.
    """
    url = f"https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {LLAMA_API_KEY}"}

    try:
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            return result.json().get("status")
        else:
            return f"Failed to check status: {result.status_code}"
    except Exception as e:
        return f"Failed to check status: {e}"


#----------------------------Part 5 - Core Extraction Logic and Agent Tools:-----------------------------
# Core extraction and agent tools
@traceable(run_type="tool", name="Llama scraper")
def llama_parser(file_url, data_points, links_scraped):
    """
    Parse a file using the Llama API and extract structured data.
    
    Args:
    file_url (str): The URL of the file to parse.
    data_points (List[Dict]): The list of data points to extract.
    links_scraped (List[str]): List of already scraped links.
    
    Returns:
    dict: The extracted structured data or an error message.
    """
    try:
        job_id = create_parse_job(file_url)
        status = check_status(job_id)
        while status != "SUCCESS":
            status = check_status(job_id)
        markdown =  get_content(job_id)
        links_scraped.append(file_url)

        extracted_data = extract_data_from_content(markdown, data_points, links_scraped, file_url)

        return extracted_data

    except Exception as e:
        return f"Failed to parse the file: {e}"

# Web scraping function
@traceable(run_type="tool", name="Scrape")
def scrape(url, data_points, links_scraped):
    """
    Scrape a given URL and extract structured data. Also do topic research
    
    Args:
    url (str): The URL to scrape.
    data_points (List[Dict]): The list of data points to extract.
    links_scraped (List[str]): List of already scraped links.
    
    Returns:
    dict: The extracted structured data or an error message.
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    try:
        scraped_data = app.scrape_url(url)
        markdown = scraped_data["markdown"][: (max_token * 2)]
        links_scraped.append(url)

        extracted_data = extract_data_from_content(markdown, data_points, links_scraped, url)

        return extracted_data
    except Exception as e:
        print("Unable to scrape the url")
        print(f"Exception: {e}")
        return "Unable to scrape the url"

@traceable(run_type="tool", name="Internet search")
def search(query, links_scraped, data_points):
    """
    Perform an internet search and topic research andextract structured data from the results.
    
    Args:
    query (str): The search query.
    links_scraped (List[str]): List of already scraped links.
    data_points (List[Dict]): The list of data points to extract.
    
    Returns:
    dict: The extracted structured data or an error message.
    """
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    params = {"pageOptions": {"fetchPageContent": True}}

    try:
        search_result = app.search(query, params=params)
        print("search result found")

        max_char = int(max_token * 2)
        search_result_str = str(search_result)[:max_char]

        FilteredModel = create_filtered_model(data_points, DataPoints, links_scraped)

        ExtendedDataPoints = create_model(
            'DataPoints',
            reference_links=(List[str], Field([], description=f"Reference links where we collected data points for other fields")),
            __base__=FilteredModel
        )

        # Patch the OpenAI client
        client = instructor.from_openai(OpenAI())

        # Extract structured data from natural language
        result = client.chat.completions.create(
            model=GPT_MODEL,
            response_model=ExtendedDataPoints,
            messages=[{"role": "user", "content": search_result_str}],
        )

        filtered_data = filter_empty_fields(result)
        
        data_to_update = [
            {"name": key, "value": value["value"], "reference": filtered_data["reference_links"]["value"] ,"type": value["type"]}
            for key, value in filtered_data.items() if key != 'relevant_urls_might_contain_further_info'
        ]

        update_data(data_points, data_to_update)

        return result.json()
    except Exception as e:
        print("Unable to scrape the url")
        print(f"Exception: {e}")
        return "Unable to search this query"

@traceable(run_type="tool", name="Update data points")
def update_data(data_points, extracted_data):
    """
    Update data_points with extracted information
    """
    for point in data_points:
        name = point['name']
        if name in extracted_data:
            point['value'] = extracted_data[name]
            point['reference'] = extracted_data.get('reference', None)




@traceable(run_type="llm", name="Agent chat completion")
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tool_choice, tools, model=GPT_MODEL):
    """
    Make a chat completion request to the OpenAI API.

    Args:
        messages (List[Dict]): The conversation history.
        tool_choice (str): The chosen tool for the AI to use.
        tools (List[Dict]): Available tools for the AI to use.
        model (str): The GPT model to use.

    Returns:
        openai.ChatCompletion: The response from the OpenAI API.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(message):
    """
    Print a conversation message with color-coding based on the role.

    Args:
        message (Dict): The message to print.
    """
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }

    if message["role"] == "system":
        print(colored(f"system: {message['content']}", role_to_color[message["role"]]))
    elif message["role"] == "user":
        print(colored(f"user: {message['content']}", role_to_color[message["role"]]))
    elif message["role"] == "assistant" and message.get("tool_calls"):
        print(
            colored(
                f"assistant: {message['tool_calls']}\n",
                role_to_color[message["role"]],
            )
        )
    elif message["role"] == "assistant" and not message.get("tool_calls"):
        print(
            colored(
                f"assistant: {message['content']}\n", role_to_color[message["role"]]
            )
        )
    elif message["role"] == "tool":
        print(
            colored(
                f"function ({message['name']}): {message['content']}\n",
                role_to_color[message["role"]],
            )
        )

# Dictionary of available tools
tools_list = {
    "scrape": scrape,
    "search": search,
    "update_data": update_data,
    "file_reader": llama_parser,
}

@traceable(name="Optimise memory")
def memory_optimise(messages: list):
    """
    Optimize the conversation history to fit within token limits.

    Args:
        messages (List[Dict]): The full conversation history.

    Returns:
        List[Dict]: The optimized conversation history.
    """
    system_prompt = messages[0]["content"]

    # token count
    encoding = tiktoken.encoding_for_model(GPT_MODEL)

    if len(encoding.encode(str(messages))) > max_token:
        latest_messages = messages
        token_count_latest_messages = len(encoding.encode(str(latest_messages)))
        print(f"initial Token count of latest messages: {token_count_latest_messages}")

        while token_count_latest_messages > max_token:
            latest_messages.pop(0)
            token_count_latest_messages = len(encoding.encode(str(latest_messages)))
            print(f"Token count of latest messages: {token_count_latest_messages}")

        print(f"Final Token count of latest messages: {token_count_latest_messages}")

        index = messages.index(latest_messages[0])
        early_messages = messages[:index]

        prompt = f""" {early_messages}
        -----
        Above is the past history of conversation between user & AI, including actions AI already taken
        Please summarise the past actions taken so far, specifically around:
        - What data source have the AI look up already
        - What data points have been found so far

        SUMMARY:
        """

        response = client.chat.completions.create(
            model=GPT_MODEL, messages=[{"role": "user", "content": prompt}]
        )

        system_prompt = f"""{system_prompt}; Here is a summary of past actions taken so far: {response.choices[0].message.content}"""
        messages = [{"role": "system", "content": system_prompt}] + latest_messages

        return messages

    return messages

@traceable(name="Call agent")
def call_agent(prompt, system_prompt, tools, plan, data_points, entity_name, links_scraped):
    """
    Call the AI agent to perform tasks based on the given prompt and tools.

    Args:
        prompt (str): The user's prompt.
        system_prompt (str): The system instructions for the AI.
        tools (List[Dict]): Available tools for the AI to use.
        plan (bool): Whether to create a plan before execution.
        data_points (List[Dict]): The list of data points to extract.
        entity_name (str): The name of the entity being researched.
        links_scraped (List[str]): List of already scraped links.

    Returns:
        str: The final response from the AI agent.
    """
    messages = []

    if plan:
        messages.append(
            {
                "role": "user",
                "content": (
                    system_prompt
                    + "  "
                    + prompt
                    + "  Let's think step by step, make a plan first"
                ),
            }
        )

        chat_response = chat_completion_request(
            messages, tool_choice="none", tools=tools
        )
        messages = [
            {"role": "user", "content": (system_prompt + "  " + prompt)},
            {"role": "assistant", "content": chat_response.choices[0].message.content},
        ]

    else:
        messages.append({"role": "user", "content": (system_prompt + "  " + prompt)})

    state = "running"

    for message in messages:
        pretty_print_conversation(message)

    while state == "running":
        chat_response = chat_completion_request(messages, tool_choice=None, tools=tools)

        if isinstance(chat_response, Exception):
            print("Failed to get a valid response:", chat_response)
            state = "finished"
        else:
            current_choice = chat_response.choices[0]
            messages.append(
                {
                    "role": "assistant",
                    "content": current_choice.message.content,
                    "tool_calls": current_choice.message.tool_calls,
                }
            )
            pretty_print_conversation(messages[-1])
            
            if current_choice.finish_reason == "tool_calls":
                tool_calls = current_choice.message.tool_calls
                for tool_call in tool_calls:
                    function = tool_call.function.name
                    arguments = json.loads(
                        tool_call.function.arguments
                    )  # Parse the JSON string to a Python dict

                    if function == "scrape":
                        result = tools_list[function](
                            arguments["url"], data_points, links_scraped
                        )
                    elif function == "search":
                        result = tools_list[function](
                            arguments["query"], entity_name, data_points
                        )
                    elif function == "update_data":
                        result = tools_list[function](
                            data_points, arguments["datas_update"]
                        )
                    elif function == "file_reader":
                        result = tools_list[function](arguments["file_url"], links_scraped)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function,
                            "content": result,
                        }
                    )
                    pretty_print_conversation(messages[-1])

            if current_choice.finish_reason == "stop":
                state = "finished"

            # messages = memory_optimise(messages)

    return messages[-1]["content"]





# Function to save JSON array to a file in a pretty-printed format
def save_json_pretty(data, filename):
    """
    Save a JSON array to a file in a pretty-printed format.

    Args:
        data: The data to be saved as JSON.
        filename (str): The name of the file to save the data to.
    """
    try:
        print(f"Saving data to {filename}")
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, sort_keys=True, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")


special_instruction = "This is a scrapper for any website and can be used for any docs as well, website or docs can often exist as image screenshot or pdf file, you should scrape those files to extract the content info; Make sure you extract all the imgs that might contain website or docs info;"


def extract_data_from_content(content, data_points, links_scraped, url):
    """Extract structured data from parsed content using the GPT model."""
    try:
        prompt = f"""
        Extract comprehensive information from this content. Be thorough and detailed in your extraction.
        Include all available information for the following fields:

        - title: The main title, name, or heading
        - description: A detailed and comprehensive description
        - key_points: List of important points, features, or highlights
        - contact: All contact information including:
          * Email addresses
          * Phone numbers
          * Contact forms
          * Messaging platforms
          * Support channels
        - location: Physical location details including:
          * Full address
          * City/Region
          * Country
          * Postal/Zip code
          * Multiple locations if available
        - social_media: All social media presence:
          * LinkedIn
          * Twitter/X
          * Facebook
          * Instagram
          * YouTube
          * Other platforms
        - services: Complete list of services or products offered
        - team: Information about team members including:
          * Names
          * Roles
          * Bios
          * Contact details
        - company_info: Company details including:
          * Founding date
          * Company size
          * Industry
          * Mission/Vision
          * Values
        - technologies: Technologies, tools, platforms mentioned
        - certifications: Awards, certifications, recognitions
        - partnerships: Partner organizations or companies
        - resources: Available resources such as:
          * Documentation
          * Downloads
          * Guides
          * Whitepapers
        - metadata: Any other relevant structured information

        Content: {content}

        Please be as detailed as possible and include all information you can find. If certain information is not available, those fields can remain empty.
        """

        response = instructor_client.chat.completions.create(
            model=GPT_MODEL,
            response_model=DataPoints,
            messages=[{"role": "user", "content": prompt}]
        )

        for point in data_points:
            if hasattr(response, point['name']):
                point['value'] = getattr(response, point['name'])
                point['reference'] = url

        return data_points

    except Exception as e:
        print(f"Error in extract_data_from_content: {e}")
        return data_points

def format_response(data_points):
    """
    Format the scraped data points list into a clean dictionary
    """
    formatted_data = {}
    for point in data_points:
        name = point['name']
        value = point['value']
        formatted_data[name] = value
    return formatted_data

#----------------------------Part 6 - API Endpoints and Main Logic:-----------------------------

def send_to_api(data, domain_name, ssa, site_id):
    """Send JSON data to appropriate API endpoint"""
    # Determine API URL based on domain
    if domain_name == "projectwe.com":
        api_url = "https://projectwe.com/api/v1/langchain/pdf-upload-gallery"
    elif domain_name == "mojomosaic.xyz":
        api_url = "https://mojomosaic.xyz/api/v1/langchain/pdf-upload-gallery"
    else:
        return {"error": "Unsupported domain"}, 400

    token = "be086981-630f-4a1a-8c47-712a9e128e55"
    
    # Prepare the request
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'data': data,
        'ssa': ssa,
        'site_id': site_id
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        
        return {
            "status": "success",
            "api_response": response.json() if response.content else "Empty response from API"
        }, response.status_code
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return {"error": f"Failed to send to API: {str(e)}"}, 500
    
def save_json_file(data, filename, directory="Firecrawl_scrapper_json_files"):
    """Save JSON file to specified directory"""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath



@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data or 'ssa' not in data:
            return jsonify({
                'error': 'Missing required fields. Need "url" and "ssa"'
            }), 400

        website = data['url']
        ssa = data['ssa']
        site_id = data.get('site_id')
        domain_name = data.get("domain_name")
        
        # Initialize data points structure
        data_keys = list(DataPoints.__fields__.keys())
        data_fields = DataPoints.__fields__
        data_points = [
            {
                "name": key, 
                "value": None, 
                "reference": None, 
                "description": data_fields[key].description
            } for key in data_keys
        ]

        # Initialize links_scraped
        links_scraped = []

        # Initialize FirecrawlApp and scrape
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
        try:
            scraped_data = app.scrape_url(website)
            markdown_content = scraped_data["markdown"]
            
            # Extract data using existing function
            processed_data = extract_data_from_content(
                content=markdown_content,
                data_points=data_points,
                links_scraped=links_scraped,
                url=website
            )

            # Format the response using the processed data
            formatted_response = {
                'url': website,
                'ssa': ssa,
                'data': format_response(processed_data)
            }
            
            if site_id:
                formatted_response['site_id'] = site_id

            # Get title from processed data for filename
            title = next((item['value'] for item in processed_data if item['name'] == 'title'), 'untitled')
            filename = f"{sanitize_filename(title)}.json"
            
            # Save locally
            filepath = save_json_file(formatted_response, filename)
            print(f"Saved JSON file locally at: {filepath}")

            # Send to API if domain is specified
            api_response = None
            if domain_name:
                api_response, status_code = send_to_api(
                    data=formatted_response,
                    domain_name=domain_name,
                    ssa=ssa,
                    site_id=site_id
                )
                if status_code != 200:
                    print(f"API Response Error: {api_response}")

            # Return response
            response = {
                'data': formatted_response,
            }
            if api_response:
                response['api_response'] = api_response

            return jsonify(response), 200

        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")

    except Exception as e:
        error_response = {
            'error': str(e),
            'url': data.get('url'),
            'ssa': data.get('ssa'),
            'site_id': data.get('site_id')
        }
        return jsonify(error_response), 500

def sanitize_filename(title):
    """Convert title to a safe filename"""
    if not title:
        return 'untitled'
    # Remove special characters and replace spaces with underscores
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('-_').lower()
    return safe_title if safe_title else 'untitled'


if __name__ == '__main__':
    # Start Flask app
    app.run(debug=True, port=5008)