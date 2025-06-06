import mysql.connector
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_structured_summary(activity_name, category, resume_text, iteration):
    prompt = f"""
    Introduction: Generate detailed summaries for different activity categories based on the data in our 'resume' table. Each summary should be approximately 100 words, crafted carefully to reflect the essence of each activity's category.

    Task: Produce a JSON object (variation #{iteration+1} of 10) for activity '{activity_name}' in category '{category}' with resume text '{resume_text}'. The JSON should include the activity name, category, and a 100-word text summary explaining the essence of the category.

    Required JSON Structure:
    {{
        "activity_name": "{activity_name}",
        "category": "{category}",
        "summary": "A 100-word summary explaining the key aspects and significance of this category, including historical background, cultural relevance, and global influence."
    }}

    Specific Instructions:
    1. Make this variation #{iteration+1} different from other variations
    2. Ensure the summary is precisely 100 words
    3. Focus on the cultural and practical implications
    4. Include historical background and global influence
    5. Make it informative and tailored to the category's significance

    The output must be in valid JSON format.
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            generated_text = response.json().get("response", "")
            try:
                json_start = generated_text.find('{')
                json_end = generated_text.rfind('}') + 1
                if json_start >= 0 and json_end > 0:
                    json_str = generated_text[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON for variation {iteration+1}")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def process_resume(cursor, connection, resume_data):
    resume_id = resume_data['resume_id']
    activity_name = resume_data['activity_name']
    category = resume_data['category']
    resume_text = resume_data['resume']

    successful_variations = 0
    max_attempts = 15
    
    while successful_variations < 10 and max_attempts > 0:
        summary = generate_structured_summary(activity_name, category, resume_text, successful_variations)
        
        if summary:
            try:
                cursor.execute(
                    "INSERT INTO resume_text (resume_id, type, text) VALUES (%s, %s, %s)",
                    (resume_id, f'summary_{successful_variations+1}', json.dumps(summary))
                )
                connection.commit()
                successful_variations += 1
                logger.info(f"Generated variation {successful_variations} for {activity_name}")
            except mysql.connector.Error as err:
                logger.error(f"Database error: {err}")
                connection.rollback()
        
        max_attempts -= 1

def main():
    logger.info("Starting application")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='muaz-testing',
            ssl_disabled=False,
            use_pure=True,
            tls_versions=['TLSv1.2', 'TLSv1.3']
        )
        cursor = connection.cursor(dictionary=True)
        logger.info("Database connected")

        # Test Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": "test",
                "stream": False
            }
        )
        logger.info("Ollama connected")

        # Process resumes
        cursor.execute("SELECT * FROM resume")
        resumes = cursor.fetchall()
        logger.info(f"Found {len(resumes)} resumes")

        for resume in resumes:
            process_resume(cursor, connection, resume)

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
        logger.info("Application finished")

if __name__ == "__main__":
    main()
