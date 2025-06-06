from flask import Flask, request, jsonify
import datetime
import os
import subprocess
import time
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Flask app setup
app = Flask(__name__)

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

# Ngrok configuration
NGROK_AUTH_TOKEN = "2Mgttux7MtUhqMW5Sl0G7XruXoA_5iy9mEzwyADHLetGwkefh"
NGROK_PORT = 5000
NGROK_PATH = r"C:\Users\MUAZ\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe"  # Path to ngrok.exe

def get_calendar_service():
    """Set up and authenticate with the Google Calendar API."""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    """Check available time slots for a given date."""
    data = request.json
    print(f"Received data: {data}")  # Debug the incoming data
    
    # Check if data exists
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    date_str = data.get('date')
    print(f"Date received: {date_str}")  # Debug the date
    
    # Check if date is provided
    if not date_str:
        return jsonify({"error": "No date provided"}), 400
    
    try:
        # Parse date string into datetime object
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        # Set time bounds for the day (9 AM to 5 PM)
        start_time = date.replace(hour=9, minute=0, second=0).isoformat() + 'Z'
        end_time = date.replace(hour=17, minute=0, second=0).isoformat() + 'Z'
        
        # Get calendar service
        service = get_calendar_service()
        
        # Query Google Calendar for existing events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Generate all possible hourly slots
        all_slots = []
        for hour in range(9, 17):
            slot_start = date.replace(hour=hour, minute=0, second=0)
            slot_end = slot_start + datetime.timedelta(hours=1)
            all_slots.append({
                "start": slot_start.isoformat(),
                "end": slot_end.isoformat(),
                "formatted": f"{slot_start.strftime('%I:%M %p')} - {slot_end.strftime('%I:%M %p')}"
            })
        
        # Remove slots that overlap with existing events
        available_slots = []
        for slot in all_slots:
            is_available = True
            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Convert to comparable format if needed
                if 'T' in event_start:  # This is a datetime, not just a date
                    event_start = event_start.replace('Z', '+00:00')
                    event_end = event_end.replace('Z', '+00:00')
                
                # Check for overlap
                if (slot["start"] < event_end and slot["end"] > event_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot)
        
        # Format response as required by ElevenLabs
        return jsonify({
            "available_slots": [slot['formatted'] for slot in available_slots]
        })
        
    except Exception as e:
        print(f"Error checking availability: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule-appointment', methods=['POST'])
def schedule_appointment():
    """Schedule an appointment in Google Calendar."""
    data = request.json
    
    try:
        first_name = data.get('firstName')
        phone_number = data.get('phoneNumber')
        address = data.get('address')
        date_time = data.get('dateTime')
        
        print("\n" + "="*70, flush=True)
        print("📅 APPOINTMENT BOOKING REQUEST RECEIVED", flush=True)
        print("="*70)
        print(f"👤 Client Name: {first_name}")
        print(f"📞 Phone Number: {phone_number}")
        print(f"📍 Address: {address}")
        print(f"🕒 Requested Time: {date_time}")
        print("-"*70)
        
        # Get calendar service
        service = get_calendar_service()
        
        # Parse datetime string
        start_time = datetime.datetime.fromisoformat(date_time.replace('Z', '+00:00'))
        end_time = start_time + datetime.timedelta(hours=1)
        
        # Create event body
        event = {
            'summary': f"In-Home Estimate for {first_name}",
            'location': address,
            'description': f"In-home estimate appointment.\nPhone: {phone_number}",
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/New_York',  # Adjust for your timezone
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/New_York',  # Adjust for your timezone
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }
        
        # Insert the event
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        # Print confirmation to terminal
        print("✅ APPOINTMENT SUCCESSFULLY BOOKED!")
        print(f"📝 Event ID: {event.get('id')}")
        print(f"📝 Event Link: {event.get('htmlLink')}")
        print(f"📝 Summary: {event.get('summary')}")
        print(f"📝 Start Time: {event.get('start').get('dateTime')}")
        print(f"📝 End Time: {event.get('end').get('dateTime')}")
        print(f"📝 Location: {event.get('location')}")
        print("="*70 + "\n")
        
        return jsonify({
            "success": True,
            "appointment_details": {
                "event_id": event.get('id'),
                "summary": event.get('summary'),
                "start_time": event.get('start').get('dateTime'),
                "end_time": event.get('end').get('dateTime'),
                "location": event.get('location'),
                "html_link": event.get('htmlLink')
            }
        })
        
    except Exception as e:
        print(f"\n❌ ERROR SCHEDULING APPOINTMENT: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def start_ngrok():
    """Start ngrok and return the public URL"""
    # Configure ngrok authentication
    subprocess.run([NGROK_PATH, "config", "add-authtoken", NGROK_AUTH_TOKEN], check=True)
    
    # Start ngrok in the background
    ngrok_process = subprocess.Popen(
        [NGROK_PATH, "http", str(NGROK_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for ngrok to start and get the public URL
    time.sleep(3)  # Give ngrok time to start
    
    try:
        # Get the ngrok tunnel information
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        
        if tunnels:
            # Find HTTPS tunnel
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    ngrok_url = tunnel["public_url"]
                    return ngrok_url, ngrok_process
        
        print("No ngrok tunnels found. Make sure ngrok is installed and working properly.")
        return None, ngrok_process
    
    except Exception as e:
        print(f"Error getting ngrok URL: {str(e)}")
        return None, ngrok_process

def run_app_with_ngrok():
    """Run the Flask app with ngrok in a single process"""
    # Start ngrok first
    ngrok_url, ngrok_process = start_ngrok()
    
    if ngrok_url:
        print("\n" + "="*50)
        print(f"✅ NGROK PUBLIC URL: {ngrok_url}")
        print(f"✅ Use these URLs in ElevenLabs:")
        print(f"   - Check Availability: {ngrok_url}/api/check-availability")
        print(f"   - Schedule Appointment: {ngrok_url}/api/schedule-appointment")
        print("="*50 + "\n")
    
    # Start the Flask app in the main thread
    try:
        app.run(debug=True, port=NGROK_PORT, use_reloader=False)
    finally:
        # Clean up ngrok when Flask exits
        if ngrok_process:
            ngrok_process.terminate()

if __name__ == '__main__':
    # Run everything
    run_app_with_ngrok()