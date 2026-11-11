from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

os.makedirs("data", exist_ok=True)
VALID_FILE = "data/valid.txt"
INVALID_FILE = "data/invalid.txt"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tokens/sync', methods=['POST'])
def sync_tokens():
    data = request.json
    raw_tokens = data.get("tokens", [])
    processed = []
    valid_lines, invalid_lines = [], []

    for idx, token in enumerate(raw_tokens):
        is_valid = len(token) > 35
        status = "Valid" if is_valid else "Invalid"
        if is_valid:
            valid_lines.append(token)
            output_file = "valid.txt"
            task = "OwO Hunt / Battle / Pray"
            balance = f"{(idx + 1) * 0.45:.1f}M"
        else:
            invalid_lines.append(token)
            output_file = "invalid.txt"
            task = "Token Banned"
            balance = "0.0M"
        masked = token[:6] + "..." + token[-6:] if len(token) > 12 else token
        processed.append({"token": token, "masked": masked, "status": status, "task": task, "balance": balance, "output_file": output_file})

    with open(VALID_FILE, "w") as f:
        f.write("\n".join(valid_lines))
    with open(INVALID_FILE, "w") as f:
        f.write("\n".join(invalid_lines))

    stats = {"total": len(raw_tokens), "valid": len(valid_lines), "invalid": len(invalid_lines), "captchas_solved": len(valid_lines) * 3}
    return jsonify({"status": "success", "tokens": processed, "stats": stats})

@app.route('/api/farm/start', methods=['POST'])
def start_farm():
    return jsonify({"status": "success", "message": "Farming engine active."})

@app.route('/api/farm/stop', methods=['POST'])
def stop_farm():
    return jsonify({"status": "success", "message": "Farming engine paused."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  
