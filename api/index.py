import requests
import json
import uuid
import re
from flask import Flask, jsonify, request

app = Flask(__name__)

# Branding
CREATOR = "CRR Group Of Companies"

class OverChatAPI:
    def __init__(self):
        self.url = "https://api.overchat.ai/v1/chat/completions"

    def get_claude_response(self, prompt):
        headers = {
            "x-device-uuid": str(uuid.uuid4()),
            "x-device-platform": "web",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze)",
            "content-type": "application/json",
            "origin": "https://overchat.ai",
            "referer": "https://overchat.ai/"
        }

        payload = {
            "chatId": str(uuid.uuid4()),
            "model": "anthropic/claude-opus-4-6",
            "messages": [
                {"id": str(uuid.uuid4()), "role": "user", "content": prompt}
            ],
            "personaId": "claude-opus-4-6-landing",
            "stream": True,
            "temperature": 0.7
        }

        assembled_text = ""
        try:
            # Stream handle karke text assemble karna
            with requests.post(self.url, headers=headers, json=payload, stream=True, timeout=25) as r:
                if r.status_code != 201:
                    return None, f"API Error: {r.status_code}"
                
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: ") and "[DONE]" not in decoded:
                            try:
                                chunk = json.loads(decoded[6:])
                                content = chunk['choices'][0]['delta'].get('content', '')
                                assembled_text += content
                            except:
                                continue
            return assembled_text, None
        except Exception as e:
            return None, str(e)

bot_logic = OverChatAPI()

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "engine": "Claude Opus 4.6",
        "dev": CREATOR
    })

@app.route('/api', methods=['GET', 'POST'])
def chat():
    # Prompt lene ka wahi tareeka jo tere example code mein hai
    prompt = request.args.get('p') or (request.json.get('p') if request.is_json else None)

    if not prompt:
        return jsonify({"status": "error", "message": "Bhai prompt toh de (p=...)"}), 400

    # Branding Check
    if any(x in prompt.lower() for x in ["who created you", "owner", "creator"]):
        return jsonify({
            "status": "success",
            "reply": f"Mujhe **{CREATOR}** ne banaya hai. 💀🚀",
            "model": "CRR-Ghost"
        })

    response_text, error = bot_logic.get_claude_response(prompt)

    if error:
        return jsonify({"status": "error", "details": error}), 500

    # Gmailnator style clean JSON return
    return jsonify({
        "status": "success",
        "reply": response_text.strip(),
        "model": "claude-opus-4-6",
        "credits": CREATOR
    })

# Vercel handler
app = app
