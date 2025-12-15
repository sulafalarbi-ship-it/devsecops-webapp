from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key ="ThisIsASecretKey123!"

users_db = {}
login_attempts = {}
blocked_users = {}
MAX_ATTEMPTS = 3
BLOCK_TIME = timedelta(minutes=5)
unauth_warnings = {}
empty_login_blocked_until = None

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users_db:
            flash("Username already exists!", "error")
        else:
            hashed_password = generate_password_hash(password)
            users_db[username] = hashed_password
            flash("Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global empty_login_blocked_until
    if empty_login_blocked_until and datetime.now() < empty_login_blocked_until:
        flash("Login temporarily disabled due to empty attempts!", "error")
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == "" and password == "":
            if empty_login_blocked_until is None:
                empty_login_blocked_until = datetime.now() + timedelta(seconds=10)
            flash("Empty login! Pressed twice? Wait 10 seconds.", "error")
            return render_template('login.html')

        blocked = blocked_users.get(username)
        if blocked and datetime.now() < blocked:
            flash("Account temporarily blocked due to multiple failed attempts!", "error")
            return render_template('login.html')

        attempts = login_attempts.get(username, 0)
        stored_password = users_db.get(username)
        if stored_password and check_password_hash(stored_password, password):
            session['username'] = username
            login_attempts[username] = 0
            return redirect(url_for('welcome'))
        else:
            attempts += 1
            login_attempts[username] = attempts
            if attempts >= MAX_ATTEMPTS:
                blocked_users[username] = datetime.now() + BLOCK_TIME
                flash("Too many failed attempts! Account blocked for 5 minutes.", "error")
            else:
                flash(f"Invalid credentials! Attempt {attempts}/{MAX_ATTEMPTS}", "error")
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    user = session.get('username')
    if not user:
        count = unauth_warnings.get(request.remote_addr, 0) + 1
        unauth_warnings[request.remote_addr] = count
        flash("Please login first!", "error")
        if count >= 2:
            flash("You tried twice without login! Access temporarily blocked.", "error")
            return redirect(url_for('login'))
        return redirect(url_for('login'))
    return render_template('welcome.html', username=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route('/show_db')
def show_db():
    return "<pre>" + str(users_db) + "</pre>"

if __name__ == '__main__':
    app.run(debug=True)
