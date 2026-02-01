import os
import re
from flask import Flask, request, jsonify, session
from sambanova import SambaNova
from flask_cors import CORS

# -------------------------------
# Flask setup
# -------------------------------
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# -------------------------------
# SambaNova client
# -------------------------------
client = SambaNova(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

# -------------------------------
# System prompt for tech assistant
# -------------------------------
SYSTEM_PROMPT = "You are ByteClinic AI, a helpful tech assistant. Respond clearly, politely, and concisely."

# -------------------------------
# Helper functions
# -------------------------------
def clean_text(text: str) -> str:
    """Remove unusual characters to avoid API issues."""
    return re.sub(r"[^\w\s.,?!]", "", text)

def safe_reply(text: str) -> str:
    """Limit reply length and prevent crashes."""
    if not text:
        return "Sorry, I couldn't generate a reply."
    return text[:400]  # max 400 chars

# -------------------------------
# Chat endpoint
# -------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = clean_text(data.get("message", "").strip())

    if not message:
        return jsonify({"reply": "Please send a message."})

    # Initialize per-session history
    if "history" not in session:
        session["history"] = []

    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session["history"] + [{"role": "user", "content": message}]

    try:
        # Call SambaNova API
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct",
            messages=messages,
            max_tokens=200,
        )
        reply = safe_reply(response.choices[0].message.content)

        # Save conversation in session memory
        session["history"].append({"role": "user", "content": message})
        session["history"].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        # Log the real error for debugging
        print("SambaNova API error:", e)
        return jsonify({"reply": "Server error. Please try again."}), 500

# -------------------------------
# Health check endpoint
# -------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Server is running!"})

# -------------------------------
# Vercel serverless handler
# -------------------------------
def handler(request, context):
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=request.headers,
        data=request.body
    ):
        return app.full_dispatch_request()
