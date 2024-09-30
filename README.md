# API Speed Test

This project compares the response times of different AI language models (Mistral, Groq, and Gemini) for a given query.

## Description

The `api-speed.py` script sends a query to three different AI APIs (Mistral, Groq, and Gemini) simultaneously and measures their response times. It uses asynchronous programming to make concurrent API calls, allowing for efficient comparison of the APIs' performance.

## Prerequisites

- Python 3.7+
- API keys for Mistral, Groq, and Google (for Gemini)

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   Create a file named `api.key` in the project root directory and add your API keys:
   ```bash
   MISTRAL_API_KEY=your_mistral_api_key
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

## Usage

Run the script with: