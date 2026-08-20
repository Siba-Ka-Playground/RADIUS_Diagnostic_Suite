import socket
import threading
import webbrowser
import pyotp
from flask import Flask, request, jsonify, render_template
from core.radius_engine import RadiusEngine

app = Flask(__name__)

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

@app.route('/')
def index():
    # Pass the local machine IP to the template as a helpful default for NAS-IP
    return render_template('index.html', default_nas=get_local_ip())

@app.route('/api/primary', methods=['POST'])
def primary_auth():
    data = request.json
    
    # Extract Server Configs from the Frontend Payload
    server = data.get('server_ip')
    secret = data.get('shared_secret')
    nas_ip = data.get('nas_ip')
    
    if not server or not secret:
        return jsonify({
            "status": "error", 
            "logs": [{"color": "c-red", "msg": "[FATAL] Server Configuration (IP and Secret) is missing."}]
        })

    engine = RadiusEngine(server, secret, nas_ip)
    result = engine.transmit_auth(data['username'], data['password'])
    
    # Auto-TOTP Generation Injection
    if result.get('status') == 'challenge' and data.get('totp_secret'):
        try:
            result['logs'].append({"color": "c-gray", "msg": "[DEBUG] Generating standard RFC 6238 TOTP token..."})
            totp = pyotp.TOTP(data['totp_secret'].replace(" ", ""))
            result['auto_token'] = totp.now()
            result['logs'].append({"color": "c-blue", "msg": f"[INFO] Token Generated: {result['auto_token']}"})
        except Exception as e:
            result['logs'].append({"color": "c-red", "msg": f"[FAIL] TOTP Generation failed: {e}"})
            
    return jsonify(result)

@app.route('/api/mfa', methods=['POST'])
def mfa_auth():
    data = request.json
    
    # Extract Server Configs from the Frontend Payload
    server = data.get('server_ip')
    secret = data.get('shared_secret')
    nas_ip = data.get('nas_ip')
    
    engine = RadiusEngine(server, secret, nas_ip)
    
    user_input = data['mfa_input']
    logs_prepend = []
    
    if user_input.lower() == "auto-totp" and data.get('totp_secret'):
        totp = pyotp.TOTP(data['totp_secret'].replace(" ", ""))
        user_input = totp.now()
        logs_prepend.append({"color": "c-blue", "msg": f"[INFO] Token Generated: {user_input}"})

    result = engine.transmit_auth(data['username'], user_input, data.get('state_hex'))
    result['logs'] = logs_prepend + result['logs']
    
    return jsonify(result)

if __name__ == '__main__':
    print("[*] Launching ZTAA RADIUS Diagnostic Suite...")
    threading.Timer(1.0, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()
    app.run(host='127.0.0.1', port=5000, debug=False)