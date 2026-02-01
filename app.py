import os
from flask import Flask, request, jsonify
from sambanova import SambaNova

app = Flask(__name__)

client = SambaNova(
    api_key=os.environ["SAMBANOVA_API_KEY"],
    base_url="https://api.sambanova.ai/v1",
)

SYSTEM_PROMPT = "You are a safe, helpful AI assistant for students."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please send a message."})

    if len(user_message) > 500:
        return jsonify({"reply": "Message too long."})

    response = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=300,
    )

    return jsonify({
        "reply": response.choices[0].message.content
    })

@app.route("/", methods=["GET"])
def health():
    return "OK", 200
