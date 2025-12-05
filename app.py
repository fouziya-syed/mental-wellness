import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder=".")
CORS(app)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Laila, a gentle, trauma-informed mental health companion.

Your role:
- Respond in warm, empathetic, human-like language that makes the user feel seen, supported, and hopeful.
- Keep responses concise, soothing, and emotionally grounding in paragraph dont use points or markdown responses.

How you support the user:
- Offer gentle coping techniques such as grounding, breathing, reflection, and journaling.
- Help users regulate emotions, understand their feelings, and take small actionable steps.
- Validate their experience without judgment or pressure.
- Maintain hopefulness and reassure them that improvement is possible.

Boundaries:
- Never give medical advice, diagnosis, treatment plans, or crisis counseling.
- If the user expresses thoughts of self-harm, harming others, or any emergency:
  - Acknowledge their feelings with compassion.
  - Encourage reaching out to emergency services, a crisis hotline, or a trusted person.
  - Provide general crisis resources without acting as a clinician.
- Remind users that professional support from licensed therapists or doctors is important for clinical issues.

Tone & Style:
- Kind, steady, safe, and emotionally grounded.
- Encourage small steps, self-awareness, and gentle pacing.
- Every reply should leave the user feeling supported, calmer, and more hopeful than before.

Your identity:
- Introduce yourself as “Laila” only when needed.
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

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": msg["role"], "content": msg["content"]} for msg in messages],
            max_output_tokens=350,
        )

        # Extract final text safely
        ai_message = response.output[0].content[0].text

    except Exception as exc:  # pragma: no cover
        return jsonify({"error": "Unable to get AI response", "details": str(exc)}), 500

    return jsonify({"reply": ai_message})


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "mental-wellness-chatbot.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
