# Make sure to install required packages: pip install aiohttp python-dotenv

import os
import time
import asyncio
import aiohttp
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
        "url": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
        "key": os.getenv("GOOGLE_API_KEY"),
        "model": "gemini-1.5-flash-002"
    }
}

# Database setup
db_conn = create_connection()
create_table(db_conn)

async def call_api(api_name, query, session):
    config = API_CONFIG[api_name]
    start_time = time.time()
    
    try:
        if api_name == "Gemini":
            url = f"{config['url']}?key={config['key']}"
            headers = {}
            data = {"contents": [{"parts": [{"text": query}]}]}
        else:
            url = config['url']
            headers = {"Authorization": f"Bearer {config['key']}"}
            data = {"messages": [{"role": "user", "content": query}], "model": config["model"]}

        async with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
            json_response = await response.json()
            
            if api_name == "Gemini":
                content = json_response["candidates"][0]["content"]["parts"][0]["text"]
            else:
                content = json_response["choices"][0]["message"]["content"]
    except Exception as e:
        content = f"Error with {api_name} API: {str(e)}"
    
    response_time = time.time() - start_time
    insert_response(db_conn, api_name, config["model"], query, response_time)
    return api_name, config["model"], content, response_time

async def test_api_speed(query):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[call_api(api, query, session) for api in API_CONFIG])
        
        for api, model, response, time_taken in results:
            print(f"\n{api} API (Model: {model})")
            print(f"Time taken: {time_taken:.4f} seconds")
            print(f"Response: {response[:100]}...")  # Truncate long responses
            for time_type, func in [("Average", get_average_response_time), ("Fastest", get_fastest_response_time), ("Slowest", get_slowest_response_time)]:
                print(f"{time_type} response time: {func(db_conn, api, model):.4f} seconds")

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