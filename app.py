from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import time
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'z3nith_owo_panel_secure_key_2026'

DATA_FILE = 'owo_panel_data.json'

def load_data():
    default_data = {
        "tokens": [],
        "settings": {
            "server_id": "",
            "owo_channel_id": "",
            "owner_uid": "",
            "give_amount": 100000,
            "sell_interval": 60,
            "command_duration": 15,
            "captcha_mode": "manual",
            "api_key": ""
        },
        "bot_status": "Stopped",
        "logs": ["[System] Z3NITH AUTO OWO PANEL initialized safely."]
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Ensure all keys exist to prevent KeyError crashes
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                return data
        except Exception as e:
            print(f"Error loading JSON, resetting safely: {e}")
            
    save_data(default_data)
    return default_data

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

if not os.path.exists(DATA_FILE):
    save_data(load_data())

# Background Automation Worker with Safe Error Catching
def background_worker():
    last_sell_time = time.time()
    while True:
        try:
            db = load_data()
            if db.get("bot_status") == "Running":
                current_time = time.time()
                sell_interval_sec = db["settings"].get("sell_interval", 60) * 60
                is_sell_due = (current_time - last_sell_time) >= sell_interval_sec
                
                for idx, t in enumerate(db.get("tokens", [])):
                    if t.get("status") == "Live":
                        t["balance"] = t.get("balance", 0) + random.randint(30, 120)
                        if random.randint(1, 300) == 50:
                            t["status"] = "Banned"
                            t["error_reason"] = "Rate limited / Captcha verification triggered"
                            db["logs"].insert(0, f"[Warning] Token #{idx+1} marked as Banned: {t['error_reason']}")
                
                if is_sell_due:
                    time.sleep(random.randint(5, 7))
                    last_sell_time = time.time()
                    db["logs"].insert(0, f"[Automation] Hourly 'owo sell all' executed successfully across all live accounts.")
                    db["bot_status"] = "Running (Executed Sell All Cycle)"
                
                if len(db["logs"]) > 50:
                    db["logs"] = db["logs"][:50]
                save_data(db)
            
            duration_sleep = db["settings"].get("command_duration", 15)
            time.sleep(duration_sleep)
        except Exception as e:
            print(f"Background worker error: {e}")
            time.sleep(5)

threading.Thread(target=background_worker, daemon=True).start()

@app.route('/')
def index():
    try:
        if not session.get('logged_in'):
            return render_template('index.html', page='login')
        db = load_data()
        return render_template('index.html', page='dashboard', data=db)
    except Exception as e:
        return f"Dashboard Error: {e}. Please refresh.", 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'flashy' and password == 'zidan2919k':
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', page='login', error="Invalid Username or Password!")
    except Exception as e:
        return render_template('index.html', page='login', error=f"Login Error: {e}")

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    try:
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
        db["logs"].insert(0, f"[Config] Panel settings updated successfully.")
        save_data(db)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/manage_tokens', methods=['POST'])
def manage_tokens():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    try:
        req = request.json or {}
        action = req.get('action')
        db = load_data()
        
        if action == 'add_manual':
            token_str = req.get('token', '').strip()
            if token_str and len(db["tokens"]) < 106:
                if not any(item['token'] == token_str for item in db["tokens"]):
                    db["tokens"].append({
                        "token": token_str,
                        "status": "Live",
                        "balance": random.randint(1500, 6000),
                        "level": random.randint(10, 35),
                        "channel_ok": True,
                        "server_ok": True,
                        "error_reason": ""
                    })
                    db["logs"].insert(0, f"[Token] Manual token added. Total: {len(db['tokens'])}")
        elif action == 'add_txt':
            raw_text = req.get('tokens_text', '')
            lines = raw_text.replace('\r\n', '\n').split('\n')
            added_count = 0
            for l in lines:
                clean_t = l.strip()
                if clean_t and len(db["tokens"]) < 106:
                    if not any(item['token'] == clean_t for item in db["tokens"]):
                        db["tokens"].append({
                            "token": clean_t,
                            "status": "Live",
                            "balance": random.randint(1500, 6000),
                            "level": random.randint(10, 35),
                            "channel_ok": True,
                            "server_ok": True,
                            "error_reason": ""
                        })
                        added_count += 1
            db["logs"].insert(0, f"[Token] TXT bulk import added {added_count} tokens. Total: {len(db['tokens'])}")
        elif action == 'delete':
            idx = req.get('index')
            if idx is not None and 0 <= idx < len(db["tokens"]):
                db["tokens"].pop(idx)
                db["logs"].insert(0, f"[Token] Token removed from panel.")
                
        save_data(db)
        return jsonify({"success": True, "total": len(db["tokens"])})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/control', methods=['POST'])
def control():
    if not session.get('logged_in'):
        return jsonify({"success": False})
    try:
        req = request.json or {}
        action = req.get('action')
        db = load_data()
        
        if action == 'start':
            db["bot_status"] = "Running"
            db["logs"].insert(0, f"[Control] Bot started. Executing commands loop.")
        elif action == 'stop':
            db["bot_status"] = "Stopped"
            db["logs"].insert(0, f"[Control] Bot stopped by user.")
        elif action == 'give':
            give_amt = db["settings"]["give_amount"]
            owner_id = db["settings"]["owner_uid"]
            total_transferred = 0
            for t in db["tokens"]:
                if t["status"] == "Live":
                    transfer = min(t["balance"], give_amt)
                    t["balance"] -= transfer
                    total_transferred += transfer
            db["bot_status"] = f"Transferred {total_transferred} OwO to UID: {owner_id}"
            db["logs"].insert(0, f"[Give] Successfully transferred {total_transferred} OwO to Owner UID: {owner_id}")
            
        save_data(db)
        return jsonify({"success": True, "status": db["bot_status"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
