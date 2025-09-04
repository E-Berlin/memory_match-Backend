from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# ====== 数据库连接 ======
def get_db_conn():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
    return conn

# ====== 初始化表 ======
def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    # 用户表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)
    # 排行榜表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        ms INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()  # 启动时创建表

# ====== 注册 ======
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user, password = data.get("username"), data.get("password")

    # 校验空值
    if not user or not password:
        return jsonify({"success": False, "msg": "Username and password cannot be empty"})

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (user,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"success": False, "msg": "Username already exists"})

    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, password))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "msg": "Registration successful"})

# ====== 登录 ======
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user, password = data.get("username"), data.get("password")

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s", (user,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and row["password"] == password:
        return jsonify({"success": True, "msg": "Login successful"})
    return jsonify({"success": False, "msg": "Username or password incorrect"})

# ====== 提交成绩 ======
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    user, ms = data.get("username"), data.get("ms")

    conn = get_db_conn()
    cur = conn.cursor()
    # 查询已有成绩
    cur.execute("SELECT * FROM records WHERE username=%s ORDER BY ms ASC LIMIT 1", (user,))
    row = cur.fetchone()
    if row:
        # 如果新成绩更快就更新
        if ms < row["ms"]:
            cur.execute("UPDATE records SET ms=%s, created_at=NOW() WHERE username=%s", (ms, user))
    else:
        cur.execute("INSERT INTO records (username, ms) VALUES (%s, %s)", (user, ms))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

# ====== 排行榜 ======
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, ms FROM records ORDER BY ms ASC LIMIT 5")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# ====== 退出登录 ======
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"msg": "Logged out successfully"})

if __name__ == "__main__":
    app.run(debug=True)
