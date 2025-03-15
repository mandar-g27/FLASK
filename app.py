from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__,template_folder="template")
socketio = SocketIO(app)

# Store connected users. Key is socket id, value is a dict with username and avatar URL.
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("connect")
def handle_connect():
    # Get the username and gender from query parameters (if provided)
    username = request.args.get("username")
    gender = request.args.get("gender")
    
    # Fallback to random if values are not provided
    if not username:
        username = f"User_{random.randint(1000,9999)}"
    if gender not in ["girl", "boy"]:
        gender = random.choice(["girl", "boy"])
    
    # Remove any extra whitespace in avatar_url (if needed)
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"
    
    users[request.sid] = {"username": username, "avatar": avatar_url}
    
    # Notify everyone that a new user joined
    emit("user_joined", {"username": username, "avatar": avatar_url}, broadcast=True)
    # Send the username to the client so it can display it
    emit("set_username", {"username": username})

@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)

@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username
        }, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)
