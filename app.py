from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    return conn

def time_ago(timestamp):
    try:
        delta = datetime.now() - datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
    except:
        delta = datetime.now() - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    if delta.days > 0:
        return f'{delta.days} days ago' if delta.days > 1 else '1 day ago'
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    if hours > 0:
        return f'{hours} hours ago' if hours > 1 else '1 hour ago'
    return f'{minutes} minutes ago' if minutes > 1 else 'just now'

app.jinja_env.filters['time_ago'] = time_ago

@app.route("/")
def index():
    status_filter = request.args.get("status", "all")
    search = request.args.get("search", "")
    sort_by = request.args.get("sort", "created_at")
    allowed_sorts = ["id", "title", "priority", "status", "category", "created_at"]
    if sort_by not in allowed_sorts:
        sort_by = "created_at"
    db = get_db()
    if search:
        tickets = db.execute(f"SELECT * FROM tickets WHERE title LIKE ? OR description LIKE ? ORDER BY {sort_by} DESC",
            (f"%{search}%", f"%{search}%")).fetchall()
    elif status_filter != "all":
        tickets = db.execute(f"SELECT * FROM tickets WHERE status = ? ORDER BY {sort_by} DESC", (status_filter,)).fetchall()
    else:
        tickets = db.execute(f"SELECT * FROM tickets ORDER BY {sort_by} DESC").fetchall()
    counts = {}
    for s in ["Open", "In Progress", "Resolved"]:
        counts[s] = db.execute("SELECT COUNT(*) FROM tickets WHERE status = ?", (s,)).fetchone()[0]
    counts["Total"] = db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    db.close()
    return render_template("index.html", tickets=tickets, current_filter=status_filter, counts=counts, search=search)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO tickets (title,description,priority,category,status,created_at) VALUES (?,?,?,?,?,?)",
            (request.form["title"], request.form["description"], request.form["priority"],
             request.form["category"], "Open", datetime.now().strftime("%Y-%m-%d %H:%M")))
        db.commit()
        db.close()
        return redirect(url_for("index"))
    return render_template("submit.html")

@app.route("/ticket/<int:tid>")
def detail(tid):
    db = get_db()
    ticket = db.execute("SELECT * FROM tickets WHERE id = ?", (tid,)).fetchone()
    db.close()
    return render_template("detail.html", ticket=ticket)

@app.route("/update/<int:tid>", methods=["POST"])
def update(tid):
    db = get_db()
    db.execute("UPDATE tickets SET status = ? WHERE id = ?", (request.form["status"], tid))
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:tid>")
def delete(tid):
    db = get_db()
    db.execute("DELETE FROM tickets WHERE id = ?", (tid,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
