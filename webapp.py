from flask import Flask, render_template
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
    return render_template("index.html")

@app.route("/register")
def open_register():
    return render_template("register.html")

@app.route("/login")
def open_login():
    return render_template("login.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)