from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域访问（方便前端本地调试）

# 临时存储（可以换成数据库，比如SQLite/MySQL）
users = {}  # { username: password }
records = []  # [ { "username": "...", "ms": 1234 } ]

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user, password = data.get("username"), data.get("password")
    if user in users:
        return jsonify({"success": False, "msg": "用户名已存在"})
    users[user] = password
    return jsonify({"success": True, "msg": "注册成功"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user, password = data.get("username"), data.get("password")
    if users.get(user) == password:
        return jsonify({"success": True, "msg": "登录成功"})
    return jsonify({"success": False, "msg": "用户名或密码错误"})

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json
    user, ms = data.get("username"), data.get("ms")
    records.append({"username": user, "ms": ms})
    # 按时间升序（越快越前）
    records.sort(key=lambda r: r["ms"])
    return jsonify({"success": True})

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(records[:5])

if __name__ == "__main__":
    app.run(debug=True)
