from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"
RECORDS_FILE = "records.json"

# ====== 辅助函数：读写 JSON ======
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # 文件存在但为空或内容错误，返回默认值
                return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== 初始化数据 ======
users = load_json(USERS_FILE, {})
records = load_json(RECORDS_FILE, [])

# ====== 注册 ======
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user, password = data.get("username"), data.get("password")

    # 基础校验
    if not user or not password:
        return jsonify({"success": False, "msg": "Username and password cannot be empty"})

    if user in users:
        return jsonify({"success": False, "msg": "Username already exists"})

    users[user] = password
    save_json(USERS_FILE, users)  # ⚡️保存到文件
    return jsonify({"success": True, "msg": "Registration successful"})

# ====== 登录 ======
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user, password = data.get("username"), data.get("password")
    if users.get(user) == password:
        return jsonify({"success": True, "msg": "Login successful"})
    return jsonify({"success": False, "msg": "Username or password incorrect"})

# ====== 提交成绩 ======
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    user, ms = data.get("username"), data.get("ms")
    # 更新已有用户成绩，如果更快就替换
    existing = next((r for r in records if r["username"] == user), None)
    if existing:
        if ms < existing["ms"]:
            existing["ms"] = ms
    else:
        records.append({"username": user, "ms": ms})
    records.sort(key=lambda r: r["ms"])
    save_json(RECORDS_FILE, records)  # 保存到文件
    return jsonify({"success": True})

# ====== 排行榜 ======
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(records[:5])

# ====== 退出登录 ======
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"msg": "Logged out successfully"})

if __name__ == "__main__":
    app.run(debug=True)
