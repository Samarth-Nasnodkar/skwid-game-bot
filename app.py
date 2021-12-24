import subprocess
from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "On"


@app.route("/vote", methods=["POST"])
def bot_vote():
    data = request.get_json()
    print("Vote received: ", data)


print("Running bot.py")
processbot = subprocess.Popen(['python', 'bot.py'])
app.run("0.0.0.0", 8080)
