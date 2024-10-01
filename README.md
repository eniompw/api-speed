# API Speed Test

This project tests the speed and responses of various AI APIs, including Mistral, Groq, and Google's Gemini.

## Setup

1. Create a file named `api.key` in the project root directory with the following content:
   ```bash
   MISTRAL_API_KEY=your_mistral_api_key
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```
   Replace `your_*_api_key` with your actual API keys.

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with:
```bash
python api-speed.py
```

The script will send a test query to Mistral, Groq, and Gemini APIs concurrently and display the response times and a snippet of each response.

## Customization

To change the test query, modify the `query` variable in the `main()` function of `api-speed.py`.

## API Models

The script currently uses the following models:
- Mistral: mistral-large-2407
- Groq: llama-3.2-90b-text-preview
- Gemini: gemini-1.5-flash-002

To change the models or add more APIs, modify the `API_CONFIG` dictionary in `api-speed.py`.

## Requirements

See `requirements.txt` for the list of required Python packages.

## Note

Ensure you have valid API keys for all the services you want to test. If you don't have a key for a particular service, the script will handle the error gracefully.
