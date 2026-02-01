from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import google.generativeai as genai

app = Flask(__name__)

# Gemini setup
genai.configure(api_key="AIzaSyAzuMF1AFn-Z3DYJMX_20A8rem_mPgvH7A")
model = genai.GenerativeModel("gemini-3-flash-preview")

DB_NAME = "enquiries.db"

# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            background TEXT,
            goal TEXT,
            concern TEXT,
            status TEXT,
            ai_summary TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------

@app.route("/")
def dashboard():
    conn = get_db_connection()
    enquiries = conn.execute("SELECT * FROM enquiries").fetchall()
    conn.close()
    return render_template("dashboard.html", enquiries=enquiries)

@app.route("/add", methods=["POST"])
def add_enquiry():
    name = request.form["name"]
    email = request.form["email"]
    background = request.form["background"]
    goal = request.form["goal"]
    concern = request.form["concern"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO enquiries (name, email, background, goal, concern, status) VALUES (?, ?, ?, ?, ?, ?)",
        (name, email, background, goal, concern, "New")
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:id>")
def delete_enquiry(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM enquiries WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/update/<int:id>", methods=["POST"])
def update_status(id):
    status = request.form["status"]
    conn = get_db_connection()
    conn.execute("UPDATE enquiries SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/ai/<int:id>")
def ai_assist(id):
    conn = get_db_connection()
    enquiry = conn.execute("SELECT * FROM enquiries WHERE id = ?", (id,)).fetchone()
    conn.close()

    prompt = f"""
You are an AI assistant helping Iron Lady’s counselling team.

Learner background:
{enquiry['background']}

Career goal:
{enquiry['goal']}

Concern:
{enquiry['concern']}

Tasks:
1. Summarize learner intent in 2–3 lines
2. Identify learner mindset (confident / confused / anxious / exploratory)
3. Suggest next action for counsellor

Use plain text. No markdown.
"""

    response = model.generate_content(prompt)
    ai_text = response.text

    conn = get_db_connection()
    conn.execute(
        "UPDATE enquiries SET ai_summary = ? WHERE id = ?",
        (ai_text, id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

# ---------------- MAIN ----------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
