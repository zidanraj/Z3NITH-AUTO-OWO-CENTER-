from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import time
import json
import os

app = Flask(__name__)
app.secret_key = 'z3nith_super_secret_owo_key_2026'

DATA_FILE = 'panel_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return {
        "clients": {},
        "announcement": "Welcome to Z3NITH AUTO OWO CENTER - PRO v1. System is fully operational!",
        "global_settings": {
            "sell_all_interval": 60
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

def background_owo_worker():
    while True:
        try:
            time.sleep(10)
        except Exception as e:
            print(f"Background worker error: {e}")

threading.Thread(target=background_owo_worker, daemon=True).start()

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
        "mode": "manually",
        "client_key": "",
        "owner_key_access": True,
        "server_id": "",
        "owo_channel_id": "",
        "give_owner_uid": "",
        "amount": 0,
        "min_delay": 3,
        "max_delay": 7,
        "status": "Idle"
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

@app.route('/api/owner/update_announcement', methods=['POST'])
def update_announcement():
    if session.get('user') != 'flashy':
        return jsonify({"success": False})
    msg = request.json.get('announcement', '')
    db = load_data()
    db['announcement'] = msg
    save_data(db)
    return jsonify({"success": True})

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    user = session.get('user')
    if not user:
        return jsonify({"success": False})
    req = request.json or {}
    db = load_data()
    
    if user == 'flashy':
        target = req.get('target_client', 'global')
        if target == 'global':
            db['global_settings']['sell_all_interval'] = req.get('sell_all_interval', 60)
        else:
            if target in db['clients']:
                db['clients'][target].update(req.get('settings', {}))
    else:
        if user in db['clients']:
            db['clients'][user].update(req.get('settings', {}))
            
    save_data(db)
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
