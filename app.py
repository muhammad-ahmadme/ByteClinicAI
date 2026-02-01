import os
from flask import Flask, request, jsonify
from sambanova import SambaNova
from flask_cors import CORS  # <- add this

app = Flask(__name__)
CORS(app)  # <- enable CORS for all routes

client = SambaNova(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = data.get("message", "")

    if not message:
        return jsonify({"reply": "Please send a message."})

    try:
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct",
            messages=[
                {"role": "system", "content": "You are ByteClinic AI, a helpful technology assistant.
You specialize in giving advice about coding, apps, computers, devices, and AI.
Always respond clearly, step-by-step when needed, and in a friendly, professional tone.
Do not give personal opinions outside tech topics.
"""."},
                {"role": "user", "content": message},
            ],
            max_tokens=200,
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": "Server error."}), 500
