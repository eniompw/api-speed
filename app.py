import os
import requests
import time
import google.generativeai as genai
from google.auth.exceptions import DefaultCredentialsError
import asyncio
import aiohttp
from dotenv import load_dotenv
from database import create_connection, insert_response, get_average_response_time, create_table

# Load the API keys from the api.key file
load_dotenv('api.key')

# Now you can access the API keys as environment variables
mistral_api_key = os.getenv('MISTRAL_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

# API configurations
API_CONFIG = {
    "Mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "key": os.environ.get("MISTRAL_API_KEY"),
        "model": "mistral-large-2407"
    },
    "Groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": os.environ.get("GROQ_API_KEY"),
        "model": "llama-3.2-90b-text-preview"
    },
    "Gemini": {
        "key": os.environ.get("GOOGLE_API_KEY"),
        "model": "gemini-1.5-flash-002"
    }
}

# Gemini setup
genai.configure(api_key=API_CONFIG["Gemini"]["key"])
gemini_model = genai.GenerativeModel(API_CONFIG["Gemini"]["model"])

# Create a global database connection
db_conn = create_connection()
create_table(db_conn)  # Ensure the table exists

async def get_api_response(api_name, query, session):
    config = API_CONFIG[api_name]
    headers = {"Authorization": f"Bearer {config['key']}"}
    data = {
        "messages": [{"role": "user", "content": query}],
        "model": config["model"]
    }
    start_time = time.time()
    try:
        async with session.post(config["url"], headers=headers, json=data) as response:
            response.raise_for_status()
            json_response = await response.json()
            
            if "choices" in json_response and len(json_response["choices"]) > 0:
                content = json_response["choices"][0]["message"]["content"]
            elif "content" in json_response:
                content = json_response["content"]
            else:
                content = f"Error: Unexpected response structure from {api_name} API"
        
    except aiohttp.ClientError as e:
        content = f"Error: {str(e)}"
    
    end_time = time.time()
    response_time = end_time - start_time
    
    # Insert the response into the database using the global connection
    insert_response(db_conn, api_name, config["model"], query, response_time)
    
    return api_name, config["model"], content, response_time

async def get_gemini_response(query):
    config = API_CONFIG["Gemini"]
    start_time = time.time()
    try:
        response = await asyncio.to_thread(gemini_model.generate_content, query)
        content = response.text
    except DefaultCredentialsError as e:
        content = f"Error: Gemini API credentials not found. {str(e)}"
    except Exception as e:
        content = f"Error: Unexpected error with Gemini API. {str(e)}"
    end_time = time.time()
    response_time = end_time - start_time
    
    # Insert the response into the database using the global connection
    insert_response(db_conn, "Gemini", config["model"], query, response_time)
    
    return "Gemini", config["model"], content, response_time

async def test_api_speed(query):
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_api_response("Mistral", query, session),
            get_api_response("Groq", query, session),
            get_gemini_response(query)
        ]
        
        for future in asyncio.as_completed(tasks):
            api, model, response, time_taken = await future
            print(f"\n{api} API (Model: {model})")
            print(f"Time taken: {time_taken:.4f} seconds")
            print(f"Response: {response[:100]}...")  # Truncate long responses
            
            # Get and print the average response time using the global connection
            avg_time = get_average_response_time(db_conn, api, model)
            print(f"Average response time: {avg_time:.4f} seconds")

async def main():
    query = "In one word, what is the capital of France?"
    print(f"Query: {query}\n")
    await test_api_speed(query)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        # Close the database connection when the script exits
        db_conn.close()
