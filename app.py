import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Database Connection
def create_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn

def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            age INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Initialize database when app starts

# Login Required Decorator
def login_required(f):
    @wraps(f)  # Ensures function retains its identity
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def index():
    conn = create_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form['name']
    email = request.form['email']
    age = request.form['age']
    conn = create_connection()
    conn.execute('INSERT INTO users (name, email, age) VALUES (?, ?, ?)', (name, email, age))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    conn = create_connection()
    if request.method == 'GET':
        user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
        conn.close()
        return render_template('edit.html', user=user)
    else:
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        conn.execute('UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?', (name, email, age, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    conn = create_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple Hardcoded Authentication
        if username == "admin" and password == "password":
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials. Try Again."

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
