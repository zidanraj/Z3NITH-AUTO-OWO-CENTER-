from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import time
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'z3nith_super_secret_quest_key_2026'

DATA_FILE = 'quest_panel_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return {
        "clients": {},
        "announcement": {
            "text": "Welcome to Z3NITH AUTO QUEST PANEL V1. System is fully operational!",
            "image": "",
            "file": ""
        },
        "global_settings": {
            "sell_all_interval": 60, # minutes
            "server_id": "",
            "owo_channel_id": "",
            "owner_id": ""
        }
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON: {e}")

if not os.path.exists(DATA_FILE):
    save_data(load_data())

# Background Automated Worker simulating OwO commands & Sell All sync
def background_quest_worker():
    while True:
        try:
            db = load_data()
            # Background loop execution simulation with anti-overlap buffer
            time.sleep(random.randint(4, 8))
        except Exception as e:
            print(f"Background worker error: {e}")

threading.Thread(target=background_quest_worker, daemon=True).start()

@app.route('/')
def index():
    try:
        user = session.get('user')
        if user:
            if user == 'flashy':
                return redirect(url_for('owner_dashboard'))
            else:
                return redirect(url_for('client_dashboard'))
        return render_template('index.html', session_user=None)
    except Exception as e:
        return f"App Error: {e}", 500

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'flashy' and password == 'zidan2919k':
        session['user'] = 'flashy'
        return redirect(url_for('owner_dashboard'))
    
    db = load_data()
    if username in db.get('clients', {}):
        client = db['clients'][username]
        if client.get('password') == password and client.get('active', True):
            session['user'] = username
            return redirect(url_for('client_dashboard'))
            
    return render_template('index.html', error="Invalid Username or Password!", session_user=None)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/owner/dashboard')
def owner_dashboard():
    if session.get('user') != 'flashy':
        return redirect(url_for('index'))
    db = load_data()
    return render_template('index.html', role='owner', data=db, session_user='flashy')

@app.route('/client/dashboard')
def client_dashboard():
    user = session.get('user')
    if not user or user == 'flashy':
        return redirect(url_for('index'))
    db = load_data()
    client_info = db.get('clients', {}).get(user, {})
    return render_template('index.html', role='client', username=user, client=client_info, data=db, session_user=user)

@app.route('/api/owner/add_client', methods=['POST'])
def add_client():
    if session.get('user') != 'flashy':
        return jsonify({"success": False, "error": "Unauthorized"})
    req = request.json or {}
    username = req.get('username')
    password = req.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Missing fields"})
        
    db = load_data()
    db['clients'][username] = {
        "password": password,
        "active": True,
        "key_mode": "manually",
        "client_key": "",
        "owner_key_granted": False,
        "server_id": "",
        "owo_channel_id": "",
        "give_owner_uid": "",
        "amount": 0,
        "duration": 5,
        "status": "Idle",
        "tokens": [],
        "analytics": {
            "valid": 0,
            "invalid": 0,
            "banned": 0,
            "live": 0,
            "working": 0
        }
    }
    save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/toggle_client/<username>', methods=['POST'])
def toggle_client(username):
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    db = load_data()
    if username in db['clients']:
        db['clients'][username]['active'] = not db['clients'][username]['active']
        save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/delete_client/<username>', methods=['POST'])
def delete_client(username):
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    db = load_data()
    if username in db['clients']:
        del db['clients'][username]
        save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/grant_key/<username>', methods=['POST'])
def grant_key(username):
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    db = load_data()
    if username in db['clients']:
        db['clients'][username]['owner_key_granted'] = True
        save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/revoke_key/<username>', methods=['POST'])
def revoke_key(username):
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    db = load_data()
    if username in db['clients']:
        db['clients'][username]['owner_key_granted'] = False
        if db['clients'][username]['key_mode'] == 'owner_key':
            db['clients'][username]['key_mode'] = 'manually'
            db['clients'][username]['status'] = 'Stopped (Owner Key Revoked)'
        save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/update_announcement', methods=['POST'])
def update_announcement():
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    req = request.json or {}
    db = load_data()
    db['announcement'] = {
        "text": req.get('text', ''),
        "image": req.get('image', ''),
        "file": req.get('file', '')
    }
    save_data(db)
    return jsonify({"success": True})

@app.route('/api/owner/update_global_settings', methods=['POST'])
def update_global_settings():
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    req = request.json or {}
    db = load_data()
    db['global_settings']['sell_all_interval'] = int(req.get('sell_all_interval', 60))
    db['global_settings']['server_id'] = req.get('server_id', '')
    db['global_settings']['owo_channel_id'] = req.get('owo_channel_id', '')
    db['global_settings']['owner_id'] = req.get('owner_id', '')
    save_data(db)
    return jsonify({"success": True})

@app.route('/api/client/update_settings', methods=['POST'])
def client_update_settings():
    user = session.get('user')
    if not user or user == 'flashy':
        return jsonify({"success": False})
    req = request.json or {}
    db = load_data()
    client = db['clients'].get(user)
    if client:
        new_mode = req.get('key_mode', client['key_mode'])
        if new_mode == 'owner_key' and not client['owner_key_granted']:
            return jsonify({"success": False, "error": "Owner key access not granted by owner!"})
        
        # If switching to manually from owner_key/client_key, stop generation
        if new_mode == 'manually' and client['key_mode'] != 'manually':
            client['status'] = 'Stopped: Switched to MANUAL verification.'
        
        client['key_mode'] = new_mode
        if new_mode == 'client_key':
            client['client_key'] = req.get('client_key', '')
            
        client['server_id'] = req.get('server_id', client['server_id'])
        client['owo_channel_id'] = req.get('owo_channel_id', client['owo_channel_id'])
        client['give_owner_uid'] = req.get('give_owner_uid', client['give_owner_uid'])
        client['amount'] = int(req.get('amount', client['amount']))
        client['duration'] = int(req.get('duration', client['duration']))
        
        save_data(db)
        return jsonify({"success": True, "status": client['status']})
    return jsonify({"success": False})

@app.route('/api/client/manage_tokens', methods=['POST'])
def client_manage_tokens():
    user = session.get('user')
    if not user or user == 'flashy':
        return jsonify({"success": False})
    req = request.json or {}
    action = req.get('action') # add, remove, bulk_txt
    db = load_data()
    client = db['clients'].get(user)
    if not client:
        return jsonify({"success": False})
        
    if action == 'add':
        token = req.get('token')
        if token and token not in client['tokens']:
            client['tokens'].append(token)
    elif action == 'remove':
        token = req.get('token')
        if token in client['tokens']:
            client['tokens'].remove(token)
    elif action == 'bulk_txt':
        tokens_list = req.get('tokens_list', [])
        for t in tokens_list:
            if t.strip() and t.strip() not in client['tokens']:
                client['tokens'].append(t.strip())
                
    # Update analytics
    total = len(client['tokens'])
    client['analytics'] = {
        "valid": total,
        "invalid": 0,
        "banned": 0,
        "live": total,
        "working": total if client['key_mode'] != 'manually' else 0
    }
    save_data(db)
    return jsonify({"success": True, "tokens": client['tokens'], "analytics": client['analytics']})

@app.route('/api/client/startup', methods=['POST'])
def client_startup():
    user = session.get('user')
    if not user or user == 'flashy':
        return jsonify({"success": False})
    req = request.json or {}
    action = req.get('action') # start, off, give
    db = load_data()
    client = db['clients'].get(user)
    if not client:
        return jsonify({"success": False})
        
    if action == 'start':
        if client['key_mode'] == 'manually':
            return jsonify({"success": False, "error": "Cannot start! Current mode is MANUAL verification."})
        client['status'] = 'Running (All OwO Commands Active)'
    elif action == 'off':
        client['status'] = 'Stopped by User'
    elif action == 'give':
        client['status'] = f"Transferring OwO to UID: {client['give_owner_uid']}"
        
    save_data(db)
    return jsonify({"success": True, "status": client['status']})

if __name__ == '__main__':
    print("========================================================")
    print("🚀 Z3NITH AUTO QUEST PANEL V1 STARTED SUCCESSFULLY")
    print("⚡ Developed by: dev_flashy")
    print("========================================================")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
