import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "memory_match.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 用户表
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    # 排行榜表
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ms INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user, password = data.get("username"), data.get("password")
    if not user or not password:
        return jsonify({"success": False, "msg": "Username and password cannot be empty"})
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (user, password))
        conn.commit()
        msg = {"success": True, "msg": "Registered successfully"}
    except sqlite3.IntegrityError:
        msg = {"success": False, "msg": "Username already exists"}
    conn.close()
    return jsonify(msg)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user, password = data.get("username"), data.get("password")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (user,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == password:
        return jsonify({"success": True, "msg": "Login successful"})
    return jsonify({"success": False, "msg": "Username or password incorrect"})

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    user, ms = data.get("username"), data.get("ms")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO records(username, ms) VALUES (?, ?)", (user, ms))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, ms FROM records ORDER BY ms ASC LIMIT 5")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"username": r[0], "ms": r[1]} for r in rows])

@app.route("/logout", methods=["POST"])
def logout():
    # 这里不需要清数据库，只是返回一个成功信息
    return jsonify({"success": True, "msg": "Logged out successfully"})

if __name__ == "__main__":
    app.run(debug=True)
