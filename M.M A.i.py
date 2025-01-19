import openai
from flask import Flask, request, render_template_string, jsonify, redirect, url_for
from googletrans import Translator
import sqlite3
import datetime

app = Flask(__name__)

# AI Credentials
MASTER_PASSWORD = "Raj18110"
openai.api_key = your-  # Replace with OpenAI API key
FOUNDER = "Mr. Raj"
CO_FOUNDER = "Mr. Adarsh"

# Admin Credentials
ADMINS = {
    "RajSingh": "22414527200927",
    "AadarshSingh": "22414527200927"
}

# AI state
ai_state = "running"

# Emotion-based responses
emotion_responses = {
    'sad': "I'm really sorry you're feeling this way. If you need someone to talk to, I'm here for you.",
    'happy': "That's awesome! I'm really happy for you! Keep shining!",
    'neutral': "I hear you. How can I help you today?"
}

# Supported languages
languages = ["English", "Mandarin Chinese", "Hindi", "Spanish", "French", "Arabic", "Bengali", "Russian", "Portuguese",
             "Urdu", "Indonesian", "German", "Japanese", "Swahili", "Marathi", "Telugu", "Turkish", "Korean", "Tamil",
             "Vietnamese"]

# SQLite Database Initialization
def init_db():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, image_count INTEGER, last_reset DATE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                      (id INTEGER PRIMARY KEY, user_id INTEGER, question TEXT, answer TEXT, timestamp DATE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS invisible_logs 
                      (id INTEGER PRIMARY KEY, user_id INTEGER, query TEXT, timestamp DATE)''')
    conn.commit()
    conn.close()

# Add a new user
def add_user(name, email, phone):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, image_count, last_reset) VALUES (?, ?, ?, ?, ?)",
                       (name, email, phone, 0, datetime.date.today()))
        conn.commit()
    conn.close()

# Store invisible logs
def store_invisible_log(email, query):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invisible_logs (user_id, query, timestamp) VALUES ((SELECT id FROM users WHERE email = ?), ?, ?)",
                   (email, query, datetime.datetime.now()))
    conn.commit()
    conn.close()

# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in ADMINS and ADMINS[username] == password:
            return redirect(url_for('admin_dashboard', username=username))
        else:
            return "Invalid username or password. Please try again.", 403
    return render_template_string('''
        <h1>Admin Login</h1>
        <form action="/admin/login" method="POST">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Login</button>
        </form>
    ''')

# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    username = request.args.get('username', 'Admin')
    return render_template_string('''
        <h1>Welcome, {{ username }}</h1>
        <p>AI State: {{ ai_state }}</p>
        <a href="/admin/shutdown">Shutdown AI</a><br>
        <a href="/admin/startup">Start AI</a><br>
        <a href="/admin/invisible_logs">View Invisible Logs</a><br>
        <a href="/admin/users">View Users</a>
    ''', username=username, ai_state=ai_state)

# Shutdown AI
@app.route('/admin/shutdown')
def shutdown_ai():
    global ai_state
    ai_state = "shutdown"
    return "AI has been shut down."

# Start AI
@app.route('/admin/startup')
def startup_ai():
    global ai_state
    ai_state = "running"
    return "AI has been started."

# View Invisible Logs
@app.route('/admin/invisible_logs')
def view_invisible_logs():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invisible_logs")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

# View Users
@app.route('/admin/users')
def view_users():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Home Page
@app.route('/')
def home():
    return render_template_string('''
        <h1>Welcome to M.M AI - Created by {{ founder }} and Co-Founded by {{ cofounder }}</h1>
        <form action="/ask" method="POST">
            Name: <input type="text" name="name" required><br>
            Email: <input type="email" name="email" required><br>
            Phone: <input type="text" name="phone" required><br>
            Query: <textarea name="query" required></textarea><br>
            Emotion: <select name="emotion">
                <option value="neutral">Neutral</option>
                <option value="happy">Happy</option>
                <option value="sad">Sad</option>
            </select><br>
            Language: <select name="language">
                {% for lang in languages %}
                    <option value="{{ lang }}">{{ lang }}</option>
                {% endfor %}
            </select><br>
            Use Invisible Tab: <input type="checkbox" name="invisible"><br>
            <button type="submit">Submit</button>
        </form>
    ''', founder=FOUNDER, cofounder=CO_FOUNDER, languages=languages)

# AI Query Handler
@app.route('/ask', methods=['POST'])
def ask():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    query = request.form['query']
    emotion = request.form['emotion']
    language = request.form['language']
    invisible = request.form.get('invisible')

    add_user(name, email, phone)
    if invisible:
        store_invisible_log(email, query)

    response = openai.Completion.create(
        engine="gpt-4",
        prompt=query,
        max_tokens=200
    )
    ai_response = response.choices[0].text.strip()
    emotion_message = emotion_responses.get(emotion, "Neutral response")
    return jsonify({'response': ai_response, 'emotion_message': emotion_message})

# Run Flask App
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)