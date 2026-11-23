# admin: internal admin panel. No login, because "only internal people can reach it".
import os

import psycopg2
from flask import Flask, jsonify
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


@app.get("/")
def home():
    return "Campus admin panel (internal only). Endpoints: /users"


@app.get("/users")
def users():
    return jsonify(query("SELECT id, username, full_name, email, password_hash FROM students ORDER BY id"))
