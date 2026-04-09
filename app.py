from flask import Flask
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



if __name__ == "__main__":
    app.run()
