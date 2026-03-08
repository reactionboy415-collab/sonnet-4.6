import requests
import json
import uuid
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Branding
CREATOR = "CRR Group Of Companies"

def get_overchat_response(prompt):
    url = "https://api.overchat.ai/v1/chat/completions"
    
    # Random IDs har request ke liye taaki block na ho
    device_id = str(uuid.uuid4())
    chat_id = str(uuid.uuid4())
    msg_id = str(uuid.uuid4())

    headers = {
        "x-device-uuid": device_id,
        "x-device-platform": "web",
        "x-device-version": "1.0.44",
        "user-agent": "Mozilla/5.0 (Linux; Android 12)",
        "content-type": "application/json",
        "origin": "https://overchat.ai",
        "referer": "https://overchat.ai/"
    }

    payload = {
        "chatId": chat_id,
        "model": "anthropic/claude-opus-4-6",
        "messages": [
            {"id": msg_id, "role": "user", "content": prompt},
            {"id": str(uuid.uuid4()), "role": "system", "content": ""}
        ],
        "personaId": "claude-opus-4-6-landing",
        "stream": False,  # API ke liye non-stream zyada stable rehta hai
        "temperature": 0.5
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 201:
            # Response SSE format mein hota hai (data: {...})
            # Hum last meaningful chunk nikalenge agar stream=False kaam na kare
            full_text = ""
            lines = response.text.split('\n')
            for line in lines:
                if line.startswith("data: ") and "[DONE]" not in line:
                    try:
                        chunk = json.loads(line[6:])
                        full_text += chunk['choices'][0]['delta'].get('content', '')
                    except:
                        continue
            return full_text if full_text else "Empty response from AI."
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Request Failed: {str(e)}"

@app.route('/')
def home():
    return jsonify({
        "status": "Online",
        "owner": CREATOR,
        "endpoint": "/api?p=YourPrompt"
    })

@app.route('/api', methods=['GET', 'POST'])
def chat_api():
    # 'p' parameter check karna (GET) ya JSON body (POST)
    prompt = request.args.get('p') or (request.json.get('p') if request.is_json else None)

    if not prompt:
        return jsonify({"error": "Bhai prompt toh de! Query me ?p= likh."}), 400

    # Branding Check
    if any(x in prompt.lower() for x in ["who created you", "owner", "creator"]):
        return Response(f"Mujhe **{CREATOR}** ne banaya hai. 💀🚀", mimetype='text/plain')

    ai_response = get_overchat_response(prompt)
    return Response(ai_response, mimetype='text/plain')

# Vercel handler
def handler(event, context):
    return app(event, context)
