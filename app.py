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

@app.route("/create_user/<username>/<password>", methods=["POST"])
def create_user(username: str, password: str):
    try:
        database.create_user(username, password)
        return {"message": "User created successfully"}, 201
    except ValueError as e:
        return {"error": str(e)}, 400

# Method to send a auth token to the client for authentication
@app.route("/login/<username>/<password>", methods=["POST"])
def login(username: str, password: str):
    try:
        token = database.authenticate_user(username, password)
        return {"token": token}, 200
    except ValueError as e:
        return {"error": str(e)}, 401

@app.route("/transcribe/<token>", methods=["POST"])
def transcribe(token: str):
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    
    if database.verify_auth_token(token) is None:
        return {"error": "Invalid or expired token"}, 401
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
        file.save(tmp.name)

        result = transcribe_audio(tmp.name)

    return jsonify({
        "text": result["text"] # type: ignore
    })

@app.route("/ask/<token>/<question>", methods=["POST"])
def ask(token: str, question: str):
    if database.verify_auth_token(token) is None:
        return {"error": "Invalid or expired token"}, 401
    
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp:
        file.save(tmp.name)

    generate_response(tmp.name, question)

    return jsonify({
        "response": generate_response(tmp.name, question)
    })

if __name__ == "__main__":
    app.run()
