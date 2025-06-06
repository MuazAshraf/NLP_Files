from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
# Load environment variables from .env file
load_dotenv('.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
redirect_uri = "mojosolo.com"


app = Flask(__name__)

API_ENDPOINT = "https://api.fireflies.ai/graphql"
API_KEY = "9aa5fb68-7963-448d-a257-2539cc5863fb"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
# Define your GraphQL query
query = """
{
  transcripts {
    id
    date
    sentences{
    text
    }
  }
}
"""

# Structure your request data
data = {
    "query": query
}

response = requests.post(API_ENDPOINT, headers=headers, json=data)

def get_latest_transcript_from_fireflies():
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    
    if response.status_code == 200:
        # Extract the transcript data from the response 
        latest_transcript = response.json().get('data').get('transcripts')[0]
        
        # Concatenate the sentences to form the full transcript text
        sentences = latest_transcript.get('sentences', [])
        full_transcript_text = " ".join(sentence['text'] for sentence in sentences)
        
        # Add the concatenated text to the latest_transcript dictionary
        latest_transcript['text'] = full_transcript_text
        return latest_transcript   
    else:
        print("Failed to fetch data from Fireflies. Status Code:", response.status_code)
        return None


def extract_information(transcript_text):
    try:
        valid_users = list(user_ids.keys())
        response = client.chat.completions.create( 
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a project management expert. Analyze the transcript and extract the following information in a structured JSON format. Only use the following valid assignees: {', '.join(valid_users)}. If an assignee is mentioned that isn't in this list, leave the assignee field as null.

                    Priority levels:
                    1 = Urgent (p1)
                    2 = High (p2)
                    3 = Normal (p3)
                    4 = Low (p4)

                    Return the information in this exact format:
                    {{
                        "project_overview": "Brief overview of the project",
                        "project_deadline": "Main project deadline",
                        "tasks": [
                            {{
                                "name": "Task name",
                                "description": "Detailed description",
                                "priority": "p1",
                                "assignee": "Name of person assigned",
                                "deadline": "Task deadline if mentioned"
                            }}
                        ],
                        "summary": "Detailed project summary"
                    }}

                    Important: Return ONLY the JSON object without any markdown formatting or code block markers."""
                },
                {
                    "role": "user",
                    "content": transcript_text
                }
            ],
            temperature=0,
            max_tokens=4096
        )
        
        # Get the raw response content
        content = response.choices[0].message.content.strip()
        
        # Clean up any potential markdown formatting
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
            content = content.strip()
            
        # Parse the cleaned JSON
        return json.loads(content)
    except Exception as e:
        print(f"Error in extract_information: {str(e)}")
        print(f"Raw content: {content}")  # Add this line for debugging
        return {
            "project_overview": "Failed to extract information",
            "project_deadline": "Unknown",
            "tasks": [],
            "summary": f"Error occurred: {str(e)}"
        }


@app.route('/')
def index():
    return render_template('clickup_transcript.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        # Verify auth first
        if not verify_auth():
            return jsonify({'error': 'ClickUp authentication failed'}), 401

        latest_transcript = get_latest_transcript_from_fireflies()
        if not latest_transcript:
            return jsonify({'error': 'Failed to fetch transcript'}), 500

        # Get the list_id from the request
        list_id = request.json.get('list_id')
        if not list_id:
            return jsonify({'error': 'list_id is required'}), 400

        extracted_info = extract_information(latest_transcript['text'])
        tasks_created = []
        
        for task in extracted_info['tasks']:
            task_response = create_task(
                list_id=list_id,
                name=task['name'],
                description=task['description'],
                priority=task['priority'],
                assignee_name=task.get('assignee')
            )
            tasks_created.append(task_response)
        
        return jsonify({
            'transcript': latest_transcript['text'],
            'project_overview': extracted_info['project_overview'],
            'project_deadline': extracted_info['project_deadline'],
            'summary': extracted_info['summary'],
            'tasks': tasks_created
        })
    except Exception as e:
        print(f"Error in get_transcript: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


CLICKUP_TOKEN = '44183335_507a749059557a8f5a99973e7cb8f6c85fe38a6f627cf651b934ac86dcfa98ea'
team_id = "8409074"
BASE_URL = "https://api.clickup.com/api/v2/"
HEADERS = {
    "Authorization": CLICKUP_TOKEN, 
    "Content-Type": "application/json"
}

@app.route('/clickup_agent')
def clickup_agent():
    return render_template('clickup.html')

def fetch_spaces():
    url = f"{BASE_URL}team/{team_id}/space"
    response = requests.get(url, headers=HEADERS)
    return response.json()

@app.route('/get_spaces', methods=['GET'])
def get_spaces():
    spaces_data = fetch_spaces()
    return jsonify(spaces_data)

def create_folder(space_id, name):
    url = f"{BASE_URL}space/{space_id}/folder"
    data = {
        "name": name
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def create_list(folder_id, name):
    url = f"{BASE_URL}folder/{folder_id}/list"
    data = {
        "name": name
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

def verify_auth():
    """Verify authentication and get correct team ID"""
    url = f"{BASE_URL}user"  # Use user endpoint to get authorized teams
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Auth Error: {response.json()}")
        return False
    
    # Get the teams the user has access to
    user_data = response.json()
    teams = user_data.get('teams', [])
    
    if not teams:
        print("No teams found for this user")
        return False
        
    # Update global team_id with the first available team
    global team_id
    team_id = str(teams[0]['id'])
    print(f"Using team ID: {team_id}")
    return True

def create_task(list_id, name, description, priority, assignee_name):
    try:
        # Verify auth and get correct team ID
        if not verify_auth():
            return {
                "error": "Authentication failed. Please check your ClickUp token and permissions."
            }
        
        # Convert priority to ClickUp format
        priority_map = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            "p1": 1,
            "p2": 2,
            "p3": 3,
            "p4": 4,
            "urgent": 1,
            "high": 2,
            "normal": 3,
            "low": 4
        }
        
        # Convert priority to string and lowercase for matching
        if isinstance(priority, (int, str)):
            priority_key = str(priority).lower()
            clickup_priority = priority_map.get(priority_key, 3)  # Default to Normal
        else:
            clickup_priority = 3  # Default to Normal if priority is invalid
            
        assignee_id = None
        if assignee_name:
            assignee_name_lower = assignee_name.lower()
            for user_name, user_id in user_ids.items():
                if user_name.lower() == assignee_name_lower:
                    assignee_id = user_id
                    break
        
        data = {
            "name": name,
            "description": description,
            "priority": clickup_priority,
        }
        
        if assignee_id:
            data["assignees"] = [assignee_id]
        
        url = f"{BASE_URL}list/{list_id}/task"
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code != 200:
            error_data = response.json()
            print(f"Failed to create task. Status: {response.status_code}, Response: {error_data}")
            
            if error_data.get('ECODE') == 'OAUTH_027':
                return {
                    "error": "Team authorization failed. Please verify your ClickUp token has access to the correct team.",
                    "name": name,
                    "intended_assignee": assignee_name,
                    "details": error_data
                }
            return {
                "error": f"Failed to create task: {error_data}",
                "name": name,
                "intended_assignee": assignee_name
            }
            
        result = response.json()
        if not assignee_id and assignee_name:
            result["warning"] = f"Could not find user '{assignee_name}' in the system. Task created without assignee."
        
        return result
        
    except Exception as e:
        print(f"Exception in create_task: {str(e)}")
        return {
            "error": f"Failed to create task: {str(e)}",
            "name": name,
            "intended_assignee": assignee_name
        }

@app.route('/create_structure', methods=['POST'])
def create_structure():
    data = request.json
    space_id = data.get('spaceId')
    folder_name = data.get('folderName')
    list_name = data.get('listName')
    task_name = data.get('taskName')
    description = data.get('description')
    priority = data.get('priority')
    assignee_name = data.get("assignee_name")
    app.logger.debug(f"Assignee Name: {assignee_name}")
    
    folder_response = create_folder(space_id, folder_name)
    list_response = create_list(folder_response.get('id'), list_name)
    app.logger.debug(f"List Response: {list_response}")
    task_response = create_task(list_response.get('id'), task_name, description, priority, assignee_name)
    return jsonify(response=task_response, list_id=list_response.get('id'))
    

user_ids = {
    "Muaz Ashraf": 44183335,
    "Ian Matenaer": 44183332,
    "Saifullah Sohail": 72038349,
    "Jostens": 38130033,
    "ASID User": 38114073,
    "Guest User": 26394280,
    "Beau Gilles": 38105691,
    "Info Test": 32332725,
    "Henry Hoeglund": 14933310,
    "Davyd Barchuk": 32161898,
    "Cooper McKinnon": 32161897,
    "Andy Rose": 32161896,
    "Chris Handrick": 12853715,
    "Beau Gilles": 10760744,  # Note: This user is listed twice. This ID will override the previous one.
    "Nick Michael": 10760743,
    "Zain Zulifqar": 10760740,
    "Maggie Heilmann": 10760733,
    "McKinzie Plots": 10760732,
    "Christopher Benjamin": 10760731,
    "Kira Diner": 10684981,
    "Klaus Winkler": 6619186,
    "Kristine Matenaer": 10666395,
    "anna matenaer": 10520440,
    "David T Matenaer": 10518265,
    "Abubakar Khalid": 10511027
}
@app.route('/get_names', methods=['GET'])
def get_names():
    return jsonify(names=list(user_ids.keys()))



if __name__ == '__main__':
    app.run(debug=True)