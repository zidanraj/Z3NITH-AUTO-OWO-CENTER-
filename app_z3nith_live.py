from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import threading
import time

app = Flask(__name__)
app.secret_key = 'z3nith_live_owo_2026'

STATE_FILE = 'z3nith_live_state.json'
VALID_KEY = 'Z3NITH-VIP-2026'  # Grow2Pets / Z3NITH Secure Access Key

def load_state():
    default_state = {
        "activated": False,
        "tokens": [],
        "settings": {
            "server_id": "",
            "channel_id": "",
            "auto_hunt": True,
            "auto_battle": True,
            "auto_gems": True,
            "auto_gamble": False
        },
        "stats": {
            "total_tokens": 0,
            "live_tokens": 0,
            "banned": 0,
            "total_cowoncy": 500000
        },
        "bot_status": "Stopped",
        "logs": ["[System] Z3NITH Core Automation Engine synchronized successfully."]
    }
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    save_state(default_state)
    return default_state

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

# Background Worker simulating the actual owomizu loop execution
def owo_automation_worker():
    while True:
        state = load_state()
        if state.get("bot_status") == "Running" and state.get("tokens"):
            channel = state["settings"].get("channel_id")
            if channel:
                state["logs"].insert(0, f"[OwO Engine] Fired auto-hunt & battle across {len(state['tokens'])} active tokens...")
                state["stats"]["total_cowoncy"] += len(state["tokens"]) * 1500
                if len(state["logs"]) > 40:
                    state["logs"] = state["logs"][:40]
                save_state(state)
            else:
                state["logs"].insert(0, "[Warning] Channel ID missing in configuration!")
                save_state(state)
            time.sleep(15)
        else:
            time.sleep(2)

# Start background worker thread
threading.Thread(target=owo_automation_worker, daemon=True).start()

@app.route('/')
def index():
    state = load_state()
    if not state.get("activated", False):
        return render_template('z3nith_live.html', view="activate")
    return render_template('z3nith_live.html', view="dashboard", data=state)

@app.route('/activate', methods=['POST'])
def activate():
    key = request.form.get('key', '').strip()
    state = load_state()
    if key == VALID_KEY:
        state["activated"] = True
        save_state(state)
        return redirect(url_for('index'))
    return render_template('z3nith_live.html', view="activate", error="Invalid Activation Key! Use: Z3NITH-VIP-2026")

@app.route('/logout')
def logout():
    state = load_state()
    state["activated"] = False
    save_state(state)
    return redirect(url_for('index'))

@app.route('/api/control', methods=['POST'])
def control():
    req = request.json or {}
    action = req.get('action')
    state = load_state()
    if action == 'start':
        state["bot_status"] = "Running"
        state["logs"].insert(0, "[Control] Automation started. Engine loops active.")
    elif action == 'stop':
        state["bot_status"] = "Stopped"
        state["logs"].insert(0, "[Control] Automation stopped by user.")
    save_state(state)
    return jsonify({"success": True, "status": state["bot_status"]})

@app.route('/api/tokens', methods=['POST'])
def manage_tokens():
    req = request.json or {}
    action = req.get('action')
    state = load_state()
    
    if action == 'add':
        raw = req.get('tokens', '')
        new_list = [t.strip() for t in raw.splitlines() if t.strip()]
        for t in new_list:
            if t not in state["tokens"]:
                state["tokens"].append(t)
        state["stats"]["total_tokens"] = len(state["tokens"])
        state["stats"]["live_tokens"] = len(state["tokens"])
        state["logs"].insert(0, f"[Tokens] Loaded {len(new_list)} new tokens into system.")
    elif action == 'clear':
        state["tokens"] = []
        state["stats"]["total_tokens"] = 0
        state["stats"]["live_tokens"] = 0
        state["logs"].insert(0, "[Tokens] All tokens wiped clean.")
        
    save_state(state)
    return jsonify({"success": True, "stats": state["stats"]})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    req = request.json or {}
    state = load_state()
    state["settings"].update(req)
    state["logs"].insert(0, "[Config] Target Server and Channel settings saved.")
    save_state(state)
    return jsonify({"success": True})

if __name__ == '__main__':
    print("[+] Z3NITH LIVE OWO PANEL running on http://0.0.0.0:1200")
    app.run(host='0.0.0.0', port=1200, debug=True)
    
