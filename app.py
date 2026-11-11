from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import time
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'z3nith_clean_quest_key_2026'

DATA_FILE = 'clean_panel_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return {
        "tokens": [],
        "settings": {
            "server_id": "",
            "owo_channel_id": "",
            "owner_uid": "",
            "give_amount": 100000,
            "sell_interval": 60, # minutes
            "command_duration": 15, # seconds between standard command cycles (owo, hunt, battle, team, pray, etc.)
            "captcha_mode": "manual",
            "api_key": ""
        },
        "bot_status": "Stopped"
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

if not os.path.exists(DATA_FILE):
    save_data(load_data())

# Background Automation Worker with Command Durations & Anti-Overlap Sell All Buffer
def background_worker():
    last_sell_time = time.time()
    while True:
        try:
            db = load_data()
            if db["bot_status"] == "Running":
                current_time = time.time()
                sell_interval_sec = db["settings"].get("sell_interval", 60) * 60
                
                # Check if sell all is due
                is_sell_due = (current_time - last_sell_time) >= sell_interval_sec
                
                for t in db["tokens"]:
                    if t["status"] == "Live":
                        # Standard command cycle simulation (owo, hunt, battle, team, pray, daily, zoo)
                        t["balance"] = t.get("balance", 0) + random.randint(20, 100)
                
                if is_sell_due:
                    # Anti-overlap buffer: delay sell all slightly or execute after standard commands
                    time.sleep(random.randint(5, 7))
                    last_sell_time = time.time()
                    db["bot_status"] = "Running (Executed Sell All Cycle)"
                
                save_data(db)
            
            # Sleep based on user-defined command duration
            duration_sleep = db["settings"].get("command_duration", 15)
            time.sleep(duration_sleep)
        except Exception as e:
            print(f"Worker error: {e}")

threading.Thread(target=background_worker, daemon=True).start()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('index.html', page='login')
    db = load_data()
    return render_template('index.html', page='dashboard', data=db)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'flashy' and password == 'zidan2919k':
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template('index.html', page='login', error="Invalid Username or Password!")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    req = request.json or {}
    db = load_data()
    db["settings"].update({
        "server_id": req.get("server_id", ""),
        "owo_channel_id": req.get("owo_channel_id", ""),
        "owner_uid": req.get("owner_uid", ""),
        "give_amount": int(req.get("give_amount", 100000)),
        "sell_interval": int(req.get("sell_interval", 60)),
        "command_duration": int(req.get("command_duration", 15)),
        "captcha_mode": req.get("captcha_mode", "manual"),
        "api_key": req.get("api_key", "")
    })
    save_data(db)
    return jsonify({"success": True})

@app.route('/api/manage_tokens', methods=['POST'])
def manage_tokens():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    req = request.json or {}
    action = req.get('action')
    db = load_data()
    
    if action == 'add_bulk':
        raw_tokens = req.get('tokens_text', '').split('\n')
        for t_str in raw_tokens:
            clean_t = t_str.strip()
            if clean_t and len(db["tokens"]) < 106:
                if not any(item['token'] == clean_t for item in db["tokens"]):
                    db["tokens"].append({
                        "token": clean_t,
                        "status": "Live",
                        "balance": random.randint(1000, 5000),
                        "level": random.randint(5, 30),
                        "channel_ok": True,
                        "server_ok": True,
                        "error_reason": ""
                    })
    elif action == 'delete':
        idx = req.get('index')
        if idx is not None and 0 <= idx < len(db["tokens"]):
            db["tokens"].pop(idx)
            
    save_data(db)
    return jsonify({"success": True, "total": len(db["tokens"])})

@app.route('/api/control', methods=['POST'])
def control():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    req = request.json or {}
    action = req.get('action')
    db = load_data()
    
    if action == 'start':
        db["bot_status"] = "Running"
        for t in db["tokens"]:
            if t["status"] == "Live":
                if not t.get("channel_ok", True):
                    t["status"] = "Stopped"
                    t["error_reason"] = "Not in channel"
                elif not t.get("server_ok", True):
                    t["status"] = "Stopped"
                    t["error_reason"] = "Not in server"
    elif action == 'stop':
        db["bot_status"] = "Stopped"
    elif action == 'give':
        give_amt = db["settings"]["give_amount"]
        owner_id = db["settings"]["owner_uid"]
        for t in db["tokens"]:
            if t["status"] == "Live":
                transfer = min(t["balance"], give_amt)
                t["balance"] -= transfer
        db["bot_status"] = f"Transferred OwO to UID: {owner_id}"
        
    save_data(db)
    return jsonify({"success": True, "status": db["bot_status"]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
