import os
from datetime import timedelta

from flask import Flask, render_template, request, redirect, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.permanent_session_lifetime = timedelta(minutes=15)

# ================= Mongo =================
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
users = mongo.db.users

# ================= Helpers =================
def logged_in():
    return "user_id" in session

# ================= Routes =================
@app.route("/")
def home():
    if logged_in():
        return redirect("/dashboard")
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.json
        username = data["username"]
        master = data["master"]

        if users.find_one({"username": username}):
            return jsonify({"error": "User exists"}), 400

        users.insert_one({
            "username": username,
            "master": generate_password_hash(master),
            "vault": ""  # encrypted blob
        })
        return jsonify({"status": "ok"})

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        user = users.find_one({"username": data["username"]})

        if user and check_password_hash(user["master"], data["master"]):
            session.permanent = True
            session["user_id"] = str(user["_id"])
            return jsonify({"status": "ok"})

        return jsonify({"error": "Invalid credentials"}), 401

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not logged_in():
        return redirect("/")
    return render_template("dashboard.html")

@app.route("/vault", methods=["GET", "POST"])
def vault():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    user = users.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"vault": request.json.get("vault")}}
        )
        return jsonify({"status": "saved"})

    return jsonify({"vault": user.get("vault", "")})

@app.route("/backup")
def backup():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    user = users.find_one({"_id": ObjectId(session["user_id"])})
    return jsonify({
        "username": user["username"],
        "vault": user.get("vault", "")
    })

@app.route("/restore", methods=["POST"])
def restore():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    users.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"vault": request.json.get("vault")}}
    )
    return jsonify({"status": "restored"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= Run =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)