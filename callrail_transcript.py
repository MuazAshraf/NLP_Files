from flask import Flask, request, jsonify
import json
import os
import logging
from datetime import datetime
import anthropic
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Create reports directory if it doesn't exist
Path("./reports").mkdir(exist_ok=True)

# Claude API key from environment variable
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

@app.route('/webhook/callrail', methods=['POST'])
def callrail_webhook():
    """Endpoint to receive CallRail webhooks"""
    try:
        # Get webhook data
        data = request.json
        
        # Check if transcript exists
        if not data.get('transcription'):
            return jsonify({"status": "skipped", "reason": "no transcript available"}), 200
        
        # Process the transcript
        analysis_results = analyze_transcript_with_claude(data)
        
        # Save results
        save_results(data, analysis_results)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def format_transcript(data):
    """Format transcript for Claude analysis"""
    # Use conversational transcript if available (better format)
    if data.get("conversational_transcript"):
        formatted = ""
        for entry in data["conversational_transcript"]:
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("phrase", "")
            time = entry.get("start", 0)
            
            # Format as minutes:seconds
            minutes = int(time) // 60
            seconds = int(time) % 60
            formatted += f"[{minutes:02d}:{seconds:02d}] {speaker}: {text}\n\n"
        return formatted
    else:
        # Fall back to regular transcript
        return data.get("transcription", "No transcript available.")

def analyze_transcript_with_claude(call_data):
    """Send transcript to Claude for analysis"""
    try:
        # Format the transcript
        transcript = format_transcript(call_data)
        
        # Create the prompt for Claude
        prompt = f"""
        You are a professional call analyzer for a marketing agency. Review this customer service call transcript and identify:

        1. OUTCOME: Determine if the call resulted in:
           - Estimate sent
           - Job booked
           - Lead lost
        
        2. OBJECTIONS: If the lead was lost, what were the customer's main objections?
        
        3. KEY DETAILS: Extract any relevant details about the job/service requested.
        
        4. FOLLOW-UP: Recommend appropriate follow-up actions.

        TRANSCRIPT:
        {transcript}

        Format your response as JSON with the following structure:
        {{
            "outcome": "estimate_sent|job_booked|lead_lost|unclear",
            "objections": ["objection1", "objection2"],
            "job_details": "description of the job requested",
            "follow_up_recommendation": "suggested follow-up action"
        }}
        """

        # Send to Claude
        response = claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract JSON from Claude's response
        response_text = response.content[0].text
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        json_str = response_text[json_start:json_end]
        
        return json.loads(json_str)
        
    except Exception as e:
        logger.error(f"Error in Claude analysis: {str(e)}")
        return {"outcome": "analysis_failed", "error": str(e)}

def save_results(call_data, analysis_results):
    """Save analysis results to a JSON file"""
    try:
        # Create a filename with call ID and timestamp
        call_id = call_data.get("id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./reports/call_{call_id}_{timestamp}.json"
        
        # Combine relevant call data with analysis
        result = {
            "call_id": call_data.get("id"),
            "date": call_data.get("start_time"),
            "duration": call_data.get("duration"),
            "tracking_number": call_data.get("tracking_phone_number"),
            "caller_number": call_data.get("caller_number"),
            "analysis": analysis_results
        }
        
        # Write to file
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Saved analysis to {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        return None

def generate_report(days=30):
    """Generate a summary report of recent calls"""
    try:
        report_dir = Path("./reports")
        files = list(report_dir.glob("*.json"))
        
        # Initialize counters
        total = 0
        outcomes = {"estimate_sent": 0, "job_booked": 0, "lead_lost": 0, "unclear": 0, "analysis_failed": 0}
        objections = {}
        
        # Process each file
        for file in files:
            with open(file, "r") as f:
                data = json.load(f)
                
                # Count outcomes
                outcome = data.get("analysis", {}).get("outcome", "unclear")
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
                total += 1
                
                # Count objections if lead was lost
                if outcome == "lead_lost":
                    for obj in data.get("analysis", {}).get("objections", []):
                        objections[obj] = objections.get(obj, 0) + 1
        
        # Calculate conversion rate (estimates + jobs / total)
        conversion = (outcomes["estimate_sent"] + outcomes["job_booked"]) / total if total > 0 else 0
        
        # Create report
        report = {
            "total_calls": total,
            "outcomes": outcomes,
            "conversion_rate": round(conversion * 100, 2),
            "top_objections": dict(sorted(objections.items(), key=lambda x: x[1], reverse=True)[:5])
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {"error": str(e)}

# API endpoint to get reports
@app.route('/reports/summary', methods=['GET'])
def get_summary_report():
    """API endpoint to get a summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        report = generate_report(days)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)