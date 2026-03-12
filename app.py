from flask import Flask

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

if __name__ == "__main__":
    app.run()
