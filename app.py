from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import csv
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'eco_hackathon_super_secret' 

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL,
                  points INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def load_questions():
    questions = []
    filepath = os.path.join(os.path.dirname(__file__), 'dataset', 'quiz_questions.csv')
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if None in row:
                    del row[None]
                questions.append(row)
    except FileNotFoundError:
        print("Error: Could not find quiz_questions.csv")
    return questions

# --- AUTHENTICATION ROUTES ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except sqlite3.IntegrityError:
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('index'))

# --- APP ROUTES ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
        
    # FETCH ACTUAL POINTS FROM DATABASE!
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE id = ?", (session['user_id'],))
    result = c.fetchone()
    current_points = result[0] if result else 0
    conn.close()
    
    return render_template('dashboard.html', username=session['username'], points=current_points)

@app.route('/missions')
def missions():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('missions.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

# --- API ENDPOINTS ---
@app.route('/api/questions')
def get_questions():
    questions = load_questions()
    return jsonify(questions)

# NEW: SAVE SCORE API
@app.route('/api/save_score', methods=['POST'])
def save_score():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
        
    data = request.get_json()
    points_earned = data.get('score', 0)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE id = ?", (points_earned, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)