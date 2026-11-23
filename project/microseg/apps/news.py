# news: public announcements + an "image link checker" for news editors.
# The checker has a command-injection bug ON PURPOSE. It is the attacker's way in.
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

NEWS = [
    {"date": "2026-11-01", "title": "Spring registration is open"},
    {"date": "2026-11-10", "title": "Library opens 24/7 during finals"},
    {"date": "2026-11-15", "title": "Graduation project fair on 10 December"},
]


@app.get("/healthz")
def healthz():
    return "ok"


@app.get("/news")
def news():
    return jsonify(NEWS)


@app.post("/news/check-image")
def check_image():
    url = request.form.get("url", "")
    # BUG ON PURPOSE: the user's text is glued into a shell command.
    # Sending "x; id" makes the shell run curl AND id.
    command = "curl -s -o /dev/null -w '%{http_code}\\n' --max-time 3 " + url
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=20)
    return "HTTP status of image: " + result.stdout, 200, {"Content-Type": "text/plain"}
