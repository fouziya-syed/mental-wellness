import os
from flask import Flask, jsonify, request, send_from_directory
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


@app.route("/api/chat", methods=["POST"])
def chat():
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

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]} for msg in messages],
            max_output_tokens=350,
        )
        ai_message = response.output_text
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": "Unable to get AI response", "details": str(exc)}), 500

    return jsonify({"reply": ai_message})


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "mental-wellness-chatbot.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
