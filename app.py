from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# ------------------ DATABASE ------------------

def get_conn():
    return sqlite3.connect("emails.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id TEXT PRIMARY KEY,
        sender TEXT,
        subject TEXT,
        category TEXT,
        opened INTEGER DEFAULT 0,
        clicked INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM emails")
    count = cur.fetchone()[0]

    if count == 0:
        data = [
            ("1", "google", "interview call for role", "Interview", 0, 0),
            ("2", "google", "interview call for role", "Interview", 0, 0),
            ("3", "google", "interview call for internship", "Interview", 0, 0)
        ]

        cur.executemany("""
        INSERT INTO emails (id, sender, subject, category, opened, clicked)
        VALUES (?, ?, ?, ?, ?, ?)
        """, data)

    conn.commit()
    conn.close()


# 🔥 VERY IMPORTANT FOR RENDER
@app.before_request
def setup_db():
    init_db()
    seed_data()


# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "Email Tracker API is running"


@app.route("/emails")
def get_emails():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM emails")
    rows = cur.fetchall()

    emails = []
    for row in rows:
        emails.append({
            "id": row[0],
            "sender": row[1],
            "subject": row[2],
            "category": row[3],
            "opened": row[4],
            "clicked": row[5]
        })

    conn.close()
    return jsonify(emails)


@app.route("/track/<email_id>")
def track_open(email_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("UPDATE emails SET opened = opened + 1 WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()

    return "Open Tracked"


@app.route("/click/<email_id>")
def track_click(email_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("UPDATE emails SET clicked = clicked + 1 WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()

    return "Click Tracked"


@app.route("/dashboard")
def dashboard():
    email_type = request.args.get("type")

    conn = get_conn()
    cur = conn.cursor()

    if email_type:
        cur.execute("SELECT * FROM emails WHERE category = ?", (email_type,))
    else:
        cur.execute("SELECT * FROM emails")

    rows = cur.fetchall()
    conn.close()

    emails = []
    for row in rows:
        emails.append({
            "id": row[0],
            "sender": row[1],
            "subject": row[2],
            "category": row[3],
            "opened": row[4],
            "clicked": row[5]
        })

    total_emails = len(emails)
    total_opened = sum(e["opened"] for e in emails)
    total_clicked = sum(e["clicked"] for e in emails)

    open_rate = (total_opened / total_emails * 100) if total_emails > 0 else 0
    click_rate = (total_clicked / total_emails * 100) if total_emails > 0 else 0

    html = """
    <html>
    <head>
    <title>Email Dashboard</title>
    <style>
    body { font-family: Arial; margin: 40px; background-color: #f4f4f4; }
    table { border-collapse: collapse; width: 100%; background-color: white; }
    th, td { padding: 10px; text-align: left; }
    th { background-color: #333; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    a { margin-right: 10px; }
    .box { background: white; padding: 15px; margin-bottom: 20px; }
    </style>
    </head>
    <body>

    <h1>Email Dashboard</h1>

    <div class="box">
    <a href="/dashboard">All</a>
    <a href="/dashboard?type=Interview">Interview</a>
    </div>
    """

    html += f"""
    <div class="box">
    <p>Total Emails: {total_emails}</p>
    <p>Total Opens: {total_opened}</p>
    <p>Total Clicks: {total_clicked}</p>
    <p>Open Rate: {open_rate:.2f}%</p>
    <p>Click Rate: {click_rate:.2f}%</p>
    </div>
    """

    html += "<table>"
    html += "<tr><th>Sender</th><th>Subject</th><th>Category</th><th>Opened</th><th>Clicked</th></tr>"

    for email in emails:
        html += f"""
        <tr>
        <td>{email['sender']}</td>
        <td>{email['subject']}</td>
        <td>{email['category']}</td>
        <td>{email['opened']}</td>
        <td>{email['clicked']}</td>
        </tr>
        """

    html += "</table></body></html>"

    return html


# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
