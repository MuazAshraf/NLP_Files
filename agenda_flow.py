from flask import Flask, request, jsonify
import smtplib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
from datetime import datetime, timedelta 
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('.env')
import os

app = Flask(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
API_ENDPOINT = "https://api.fireflies.ai/graphql"
API_KEY = "1ae0d60c-300d-48a2-9542-bd9a61627e5c"
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
    title
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

if response.status_code == 200:
    # Successfully received data
    print(response.json())
else:
    # Handle the error
    print(f"Failed to fetch data from Fireflies. Status Code: {response.status_code}")
    print(response.text)

#get Transcript from Fireflies
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
        print(response.text)  # Printing the response content for more details
        return None

# Function to generate meeting agenda using GPT-3
def generate_agenda(transcript_text):
    meeting_date = (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y")
    meeting_time = "10:00 AM EST"
    meeting_link = "https://zoom.us/j/your-meeting-id"
    prompt = f"""Carwl carefully, read the full transcript and completely analyze the provided transcript and provide a send a deatailed agenda to client for the next meeting, Extract client names, designations, key points, and actionable discussion topics:
    
    Transcript: {transcript_text}
    
    Format the response with:
    1. A warm welcome.
    2. Names and designations of participants.
    3. Key discussion points for the next meeting.
    4. Next steps.

    Return the response in a professional email format."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        agenda_content = response.choices[0].message.content

        agenda = f"""
    Meeting Details:
    Date: {meeting_date}
    Time: {meeting_time}
    Platform: Zoom
    Join Link: {meeting_link}

    {agenda_content}

    Best regards,
    Mojo Solo
    """
        return agenda
    except Exception as e:
        print(f"Error generating agenda: {str(e)}")
        return None

# Function to send an email with the meeting agenda
def send_agenda_email(client_email, agenda):
    """Send the meeting agenda to a client via SendGrid."""
    sender_email = "muazashraf456@gmail.com"

    message = Mail(
    from_email=sender_email,
    to_emails=client_email,
    subject="Meeting Agenda",
    plain_text_content=agenda
)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {client_email} with status code {response.status_code}")
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


@app.route('/send_agenda', methods=['POST'])
def send_agenda():
    """Flask route to send agenda emails."""
    try:
        # Get client emails from the request
        client_emails = request.json.get('client_emails', [])
        if not client_emails:
            return jsonify({"error": "No client emails provided."}), 400

        # Fetch the latest transcript
        transcript = get_latest_transcript_from_fireflies()
        if not transcript:
            return jsonify({"error": "Failed to fetch transcript."}), 500

        # Generate the agenda
        agenda = generate_agenda(transcript['text'])
        if not agenda:
            return jsonify({"error": "Failed to generate agenda."}), 500

        # Send the agenda email to all clients
        email_status = []
        for email in client_emails:
            success = send_agenda_email(email, agenda)
            email_status.append({"email": email, "sent": success})

        # Check if any emails were successfully sent
        if all(not status['sent'] for status in email_status):
            return jsonify({
                "error": "Failed to send agenda emails.",
                "email_status": email_status
            }), 500

        return jsonify({
            "message": "Agenda sent successfully.",
            "email_status": email_status
        })
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to process request."}), 500

if __name__ == '__main__':
    app.run(debug=True)