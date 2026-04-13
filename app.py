import os
import tempfile
from voice_processing import transcribe_audio
from model import generate_response
from flask import Flask, jsonify, request
import database
#
#                MAIN FILE FOR SERVER
#    THIS FILE DEFINES THE API AND ITS ENDPOINTS
#

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    print("This is the vision API.")
    return "This is the vision API."

@app.route("/hello", methods=["GET"])
def hello():
    print("Hello, World!")
    return "Hello, World!"

@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    first_name = data.get("firstName")
    last_name = data.get("lastName")

    if not all([username, password, email, first_name, last_name]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        database.create_user(username, password, email, first_name, last_name)
        return jsonify({"message": "User created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    try:
        token = database.authenticate_user(username, password)
        return jsonify({"token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@app.route("/transcribe/<token>", methods=["POST"])
def transcribe(token: str):
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    
    if database.verify_auth_token(token) is None:
        return {"error": "Invalid or expired token"}, 401

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_path = tmp.name
    tmp.close()
    try:
        file.save(tmp_path)
        result = transcribe_audio(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return jsonify({
        "text": result["text"]  # type: ignore
    })

@app.route("/ask/<token>/<question>", methods=["POST"])
def ask(token: str, question: str):
    # if database.verify_auth_token(token) is None:
    #    return {"error": "Invalid or expired token"}, 401

    if "file" not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_path = tmp.name
    tmp.close()
    try:
        file.save(tmp_path)
        response = generate_response(tmp_path, question)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return jsonify({
        "response": response
    })

if __name__ == "__main__":
    app.run()
