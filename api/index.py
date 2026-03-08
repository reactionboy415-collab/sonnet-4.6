import requests
import json
import uuid
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Branding
CREATOR = "CRR Group Of Companies"

def get_ai_logic(prompt):
    url = "https://api.overchat.ai/v1/chat/completions"
    
    # Dynamic Headers & IDs
    headers = {
        "x-device-uuid": str(uuid.uuid4()),
        "x-device-platform": "web",
        "x-device-version": "1.0.44",
        "user-agent": "Mozilla/5.0 (Linux; Android 12)",
        "content-type": "application/json",
        "origin": "https://overchat.ai",
        "referer": "https://overchat.ai/"
    }

    payload = {
        "chatId": str(uuid.uuid4()),
        "model": "anthropic/claude-opus-4-6",
        "messages": [
            {"id": str(uuid.uuid4()), "role": "user", "content": prompt},
            {"id": str(uuid.uuid4()), "role": "system", "content": ""}
        ],
        "personaId": "claude-opus-4-6-landing",
        "stream": True,
        "temperature": 0.5
    }

    full_response = ""
    try:
        # Stream=True zaroori hai kyunki server data chunks mein bhej raha hai
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=25) as r:
            if r.status_code != 201:
                return f"Server Error: {r.status_code}"
            
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data_content = decoded_line[6:]
                        
                        if data_content == "[DONE]":
                            break
                        
                        try:
                            json_data = json.loads(data_content)
                            content = json_data['choices'][0]['delta'].get('content', '')
                            full_response += content
                        except:
                            continue
        return full_response if full_response else "Bhai, AI ne kuch reply nahi diya."
    except Exception as e:
        return f"Request Failed: {str(e)}"

@app.route('/api', methods=['GET', 'POST'])
def chat_api():
    prompt = request.args.get('p') or (request.json.get('p') if request.is_json else None)

    if not prompt:
        return jsonify({"error": "Prompt missing! Use ?p=YourQuery"}), 400

    # Branding Check
    if any(x in prompt.lower() for x in ["who created you", "owner", "creator"]):
        return Response(f"Mujhe **{CREATOR}** ne banaya hai. 💀🚀", mimetype='text/plain')

    result = get_ai_logic(prompt)
    return Response(result, mimetype='text/plain')

@app.route('/')
def home():
    return "CRR API is Running. Use /api?p=prompt"

# Export for Vercel
app = app
