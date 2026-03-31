from flask import Flask, request, redirect, url_for, render_template, session
import sqlite3
import cv2
import os

from face_verify import verify_face
from face_capture import capture_face
from train_model import train_model

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# ------------------ DATABASE ------------------

def init_db():
    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            aadhaar TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            voter_id TEXT NOT NULL,
            voted INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            candidate TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)

    candidates = ["Candidate A", "Candidate B", "Candidate C"]
    for c in candidates:
        cursor.execute(
            "INSERT OR IGNORE INTO votes (candidate, count) VALUES (?, 0)", (c,)
        )

    conn.commit()
    conn.close()

# ------------------ LOGIN ------------------

@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        name = request.form.get("name")
        aadhaar = request.form.get("aadhaar")
        voter_id = request.form.get("voter_id")

        conn = sqlite3.connect("voting.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, voter_id, voted FROM users WHERE aadhaar=?",
            (aadhaar,)
        )
        user = cursor.fetchone()

        if not user:
            msg = "User not registered!"

        elif user[0] != name or user[1] != voter_id:
            msg = "Details do not match!"

        elif user[2] == 1:
            msg = "You have already voted!"

        else:
            # FACE VERIFICATION
            if not verify_face(aadhaar):
                msg = "Face verification failed!"
            else:
                session["aadhaar"] = aadhaar
                conn.close()
                return redirect(url_for("vote"))

        conn.close()

    return render_template("login.html", msg=msg)

# ------------------ REGISTER ------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""

    if request.method == "POST":
        name = request.form.get("name")
        aadhaar = request.form.get("aadhaar")
        voter_id = request.form.get("voter_id")

        conn = sqlite3.connect("voting.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE aadhaar=?", (aadhaar,))
        existing_user = cursor.fetchone()

        if existing_user:
            msg = "User already registered!"
        else:
            cursor.execute(
                "INSERT INTO users (aadhaar, name, voter_id, voted) VALUES (?, ?, ?, 0)",
                (aadhaar, name, voter_id)
            )
            conn.commit()
            conn.close()

            capture_face(aadhaar)
            train_model()

            return render_template("success.html", msg="Registration Successful!")

        conn.close()

    return render_template("register.html", msg=msg)

# ------------------ VOTE ------------------

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    aadhaar = session.get("aadhaar")

    if not aadhaar:
        return redirect(url_for("login"))

    if request.method == "POST":

        candidate = request.form.get("candidate")

        conn = sqlite3.connect("voting.db")
        cursor = conn.cursor()

        cursor.execute("SELECT voted FROM users WHERE aadhaar=?", (aadhaar,))
        result = cursor.fetchone()

        if result and result[0] == 1:
            return render_template("success.html", msg="Already voted!")

        cursor.execute(
            "UPDATE votes SET count = count + 1 WHERE candidate=?",
            (candidate,)
        )

        cursor.execute(
            "UPDATE users SET voted=1 WHERE aadhaar=?",
            (aadhaar,)
        )

        conn.commit()
        conn.close()

        return render_template("success.html", msg="Vote submitted successfully!")

    return render_template("vote.html")

# ------------------ ADMIN ------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    msg = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("results"))
        else:
            msg = "Invalid admin credentials"

    return render_template("admin.html", msg=msg)

# ------------------ RESULTS ------------------

@app.route("/results")
def results():

    # ❌ BLOCK UNAUTHORIZED ACCESS
    if not session.get("admin"):
        return redirect(url_for("admin"))

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute("SELECT candidate, count FROM votes")
    data = cursor.fetchall()
    conn.close()

    max_votes = 0
    winner = ""

    for candidate, count in data:
        if count > max_votes:
            max_votes = count
            winner = candidate

    return render_template("results.html", data=data, winner=winner)

# ------------------ LOGOUT ------------------
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------ MAIN ------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)