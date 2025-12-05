# MindFlow Mental Wellness Chatbot

MindFlow is a small Flask application that serves a calming, AI-assisted mental wellness chatbot experience. The backend exposes a single chat endpoint that relays conversations to the OpenAI API using a trauma-informed system prompt, and the frontend is a polished single-page HTML file with the MindFlow interface.

## Features
- Flask API with CORS support and a `/api/chat` endpoint for streaming requests to OpenAI responses.
- Elegant single-page UI (`mental-wellness-chatbot.html`) with animated gradients and grounding exercise prompts.
- Simple configuration driven by environment variables for the port and OpenAI credentials.

## Prerequisites
- Python 3.10+
- An OpenAI API key stored in the environment variable `OPENAI_API_KEY`.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Export your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

## Running the app
Start the Flask server (defaults to port 5000):
```bash
python app.py
```
Then open the UI in your browser at [`http://localhost:5000`](http://localhost:5000). The root route serves `mental-wellness-chatbot.html` directly from the static folder.

## API
- `POST /api/chat`
  - **Request JSON**: `{ "message": "Hello", "conversation": [{"role": "user"|"assistant", "content": "..."}] }`
  - **Response JSON**: `{ "reply": "..." }` or `{ "error": "..." }` on failure.
  - The server injects a trauma-informed system prompt and forwards the conversation to the OpenAI Responses API (`gpt-4.1-mini`).

## Project structure
- `app.py` – Flask application and chat endpoint.
- `mental-wellness-chatbot.html` – Frontend UI served at `/`.
- `requirements.txt` – Python dependencies.

## Notes
- Error responses include minimal details; check server logs for debugging exceptions.
- Adjust the `PORT` environment variable to change the listening port when deploying.
