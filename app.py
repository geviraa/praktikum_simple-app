import os
import time
import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "rootpass"),
    "database": os.getenv("DB_NAME", "praktikum"),
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_conn(retries=10):
    for _ in range(retries):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.err.OperationalError:
            time.sleep(3)
    raise RuntimeError("Tidak bisa terhubung ke database")


def init_db():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS notes ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "isi VARCHAR(255) NOT NULL)"
        )
    conn.commit()
    conn.close()


@app.route("/")
def hello():
    return "Halo dari Flask + MySQL + Docker + Jenkins!"


@app.route("/notes", methods=["GET", "POST"])
def notes():
    conn = get_conn()
    with conn.cursor() as cur:
        if request.method == "POST":
            isi = (request.get_json(silent=True) or {}).get("isi", "")
            cur.execute("INSERT INTO notes (isi) VALUES (%s)", (isi,))
            conn.commit()
        cur.execute("SELECT id, isi FROM notes ORDER BY id")
        data = cur.fetchall()
    conn.close()
    return jsonify(data)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
