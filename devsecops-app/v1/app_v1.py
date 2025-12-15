from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
users_db = {}

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # حفظ البيانات بدون أي تحقق أو تشفير
        users_db[username] = password
        return redirect(url_for('welcome', username=username))
    return render_template('register.html', message=message)

@app.route('/welcome/<username>')
def welcome(username):
    return render_template('welcome.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
