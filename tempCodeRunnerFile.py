voting_open = True
from flask import Flask, request, redirect, url_for, render_template_string, session
app = Flask(__name__)
app.secret_key = "supersecretkey123"
from train_model import train_model
from face_verify import verify_face
from face_capture import capture_face
import sqlite3
def init_db():
    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            aadhaar TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            voter_id TEXT NOT NULL,
            voted INTEGER DEFAULT 0
        )
    """)
