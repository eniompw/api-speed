# API Speed Test

This project tests the speed and responses of various AI APIs, including Mistral, Groq, and Google's Gemini. It also stores the response times in a SQLite database for historical analysis.

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

3. Initialize the database:
   ```bash
   python database.py
   ```

## Usage

Run the script with:
```bash
python app.py
```

The script will send a test query to Mistral, Groq, and Gemini APIs concurrently and display:
- The response times for the current query
- A snippet of each response
- The average response time for each API/model combination
- The fastest and slowest response times ever recorded for each API/model combination

## Database

The project uses a SQLite database (`api_speed.db`) to store historical data about API responses. This allows for tracking performance over time and analyzing trends.

## Customization

To change the test query, modify the `query` variable in the `main()` function of `app.py`.

## API Models

The script currently uses the following models:
- Mistral: mistral-large-2407
- Groq: llama-3.2-90b-text-preview
- Gemini: gemini-1.5-flash-002

To change the models or add more APIs, modify the `API_CONFIG` dictionary in `app.py`.

## Requirements

See `requirements.txt` for the list of required Python packages.

## Note

Ensure you have valid API keys for all the services you want to test. If you don't have a key for a particular service, the script will handle the error gracefully and continue testing the other APIs.
