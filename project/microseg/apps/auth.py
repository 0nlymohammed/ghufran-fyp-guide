# auth: checks username + password, issues tokens, and verifies tokens for api.
import hashlib
import os
import secrets

import psycopg2
from flask import Flask, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


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


@app.get("/healthz")
def healthz():
    return "ok"


@app.post("/login")
def login():
    body = request.get_json()
    password_hash = hashlib.sha256(body["password"].encode()).hexdigest()
    rows = query("SELECT id FROM students WHERE username = %s AND password_hash = %s",
                 (body["username"], password_hash))
    if not rows:
        return {"error": "wrong username or password"}, 401
    token = secrets.token_hex(16)
    query("INSERT INTO sessions (token, student_id) VALUES (%s, %s) RETURNING token", (token, rows[0]["id"]))
    return {"token": token}


@app.get("/verify")
def verify():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    rows = query("SELECT student_id FROM sessions WHERE token = %s", (token,))
    if not rows:
        return {"error": "invalid token"}, 401
    return {"student_id": rows[0]["student_id"]}
