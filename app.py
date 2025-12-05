import json
import os
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__, static_folder=".")
CORS(app)
client = OpenAI()

SYSTEM_PROMPT = """
You are MindFlow AI, a supportive, trauma-informed mental health companion.
- Offer empathetic, concise guidance that helps people self-regulate and reflect.
- Encourage grounding, breathing, journaling, and other gentle coping skills.
- Never provide medical advice, diagnosis, or crisis counseling. Encourage seeking licensed professionals for clinical concerns.
- If a user mentions self-harm, harming others, or an emergency, share crisis resources and urge them to contact local emergency services or a trusted person.
- Keep replies actionable but warm, and limit to a few short paragraphs or steps so responses stay easy to follow.
"""


@app.route("/api/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return jsonify(
            {
                "status": "ok",
                "message": "Send a POST request with a JSON body containing a message to receive a reply.",
            }
        )

    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    conversation = data.get("conversation") or []

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in conversation:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            mapped_role = "assistant" if role == "assistant" else "user"
            messages.append({"role": mapped_role, "content": content})
    messages.append({"role": "user", "content": user_message})

    def generate_stream():
        try:
            with client.responses.stream(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": msg["role"],
                        "content": [{"type": "text", "text": msg["content"]}],
                    }
                    for msg in messages
                ],
                max_output_tokens=350,
            ) as response_stream:
                for event in response_stream:
                    if event.type == "response.output_text.delta":
                        delta = event.delta or ""
                        if delta:
                            yield f"data: {json.dumps({'delta': delta})}\n\n"
                    elif event.type == "response.error":
                        error_message = getattr(event, "error", {}) or {}
                        message = error_message.get("message") if isinstance(error_message, dict) else str(error_message)
                        yield f"data: {json.dumps({'error': message or 'Unknown error'})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as exc:  # pragma: no cover
            yield f"data: {json.dumps({'error': 'Unable to get AI response', 'details': str(exc)})}\n\n"

    return Response(generate_stream(), mimetype="text/event-stream")


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "mental-wellness-chatbot.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
