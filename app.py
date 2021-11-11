import subprocess
from flask import Flask

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "On"


print("Running bot.py")
processbot = subprocess.Popen(['python3', 'bot.py'])
app.run()