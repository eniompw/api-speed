# Make sure to install required packages: pip install aiohttp google-generativeai python-dotenv

import os
import time
import asyncio
import aiohttp
import google.generativeai as genai
from google.auth.exceptions import DefaultCredentialsError
from dotenv import load_dotenv
from database import create_connection, insert_response, get_average_response_time, create_table, get_fastest_response_time, get_slowest_response_time

# Load API keys and setup
load_dotenv('api.key')

API_CONFIG = {
    "Mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "key": os.getenv("MISTRAL_API_KEY"),
        "model": "mistral-large-2407"
    },
    "Groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": os.getenv("GROQ_API_KEY"),
        "model": "llama-3.2-90b-text-preview"
    },
    "Gemini": {
        "key": os.getenv("GOOGLE_API_KEY"),
        "model": "gemini-1.5-flash-002"
    }
}

genai.configure(api_key=API_CONFIG["Gemini"]["key"])
gemini_model = genai.GenerativeModel(API_CONFIG["Gemini"]["model"])

# Database setup
db_conn = create_connection()
create_table(db_conn)

async def call_api(api_name, query, session=None):
    config = API_CONFIG[api_name]
    start_time = time.time()
    
    try:
        if api_name == "Gemini":
            response = await asyncio.to_thread(gemini_model.generate_content, query)
            content = response.text
        else:
            headers = {"Authorization": f"Bearer {config['key']}"}
            data = {"messages": [{"role": "user", "content": query}], "model": config["model"]}
            async with session.post(config["url"], headers=headers, json=data) as response:
                response.raise_for_status()
                json_response = await response.json()
                content = json_response["choices"][0]["message"]["content"]
    except Exception as e:
        content = f"Error with {api_name} API: {str(e)}"
    
    response_time = time.time() - start_time
    insert_response(db_conn, api_name, config["model"], query, response_time)
    
    return api_name, config["model"], content, response_time

async def test_api_speed(query):
    async with aiohttp.ClientSession() as session:
        tasks = [
            call_api("Mistral", query, session),
            call_api("Groq", query, session),
            call_api("Gemini", query)
        ]
        
        results = await asyncio.gather(*tasks)
        
        for api, model, response, time_taken in results:
            print(f"\n{api} API (Model: {model})")
            print(f"Time taken: {time_taken:.4f} seconds")
            print(f"Response: {response[:100]}...")  # Truncate long responses
            avg_time = get_average_response_time(db_conn, api, model)
            fastest_time = get_fastest_response_time(db_conn, api, model)
            slowest_time = get_slowest_response_time(db_conn, api, model)
            print(f"Average response time: {avg_time:.4f} seconds")
            print(f"Fastest response time ever: {fastest_time:.4f} seconds")
            print(f"Slowest response time ever: {slowest_time:.4f} seconds")

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
