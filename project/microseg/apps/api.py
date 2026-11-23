# api: profile and grades for the logged-in student. Asks auth who owns the token.
import os

import psycopg2
import requests
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
AUTH_URL = "http://auth:5001"


def query(sql, params=()):
    """Open a DB connection, run one SQL statement, return the rows as dicts, close."""
    conn = psycopg2.connect(host="db", dbname=os.environ["POSTGRES_DB"],
                            user=os.environ["POSTGRES_USER"],
                            password=os.environ["POSTGRES_PASSWORD"], connect_timeout=3)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows


def current_student():
    """Return the student id that owns the Bearer token, or None."""
    answer = requests.get(AUTH_URL + "/verify", timeout=3,
                          headers={"Authorization": request.headers.get("Authorization", "")})
    if answer.status_code != 200:
        return None
    return answer.json()["student_id"]


@app.get("/healthz")
def healthz():
    return "ok"


@app.post("/api/login")
def login():
    answer = requests.post(AUTH_URL + "/login", json=request.get_json(), timeout=3)
    return answer.json(), answer.status_code


@app.get("/api/profile")
def profile():
    student_id = current_student()
    if student_id is None:
        return {"error": "not logged in"}, 401
    rows = query("SELECT id, full_name, email, major, year FROM students WHERE id = %s", (student_id,))
    return jsonify(rows[0])


@app.get("/api/grades")
def grades():
    student_id = current_student()
    if student_id is None:
        return {"error": "not logged in"}, 401
    rows = query("SELECT course, grade FROM grades WHERE student_id = %s ORDER BY course", (student_id,))
    return jsonify(rows)


@app.get("/api/export")
def export():
    # Old debug endpoint that nobody removed: every grade of every student, no login.
    rows = query("SELECT s.full_name, g.course, g.grade FROM grades g JOIN students s ON s.id = g.student_id ORDER BY s.id")
    return jsonify(rows)
