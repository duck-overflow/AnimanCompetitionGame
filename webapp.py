from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from flask_socketio import SocketIO
from database import insert_user

from util_funcs import delete_sessions

app = Flask(__name__, static_folder="static")

app.config["SESSION_KEY"] = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

socketio = SocketIO(app, manage_session=False)

delete_sessions()

@app.route("/")
def index():
    user = session.get("username")
    print(user)
    if user is None:
        return redirect(url_for('register'))
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        conf_email = request.form.get("conf_email")
        password = request.form.get("password")

        print(f"Test {username} {email} {conf_email} {password}")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
    
    return render_template("login.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)