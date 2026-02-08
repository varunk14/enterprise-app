import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect("tickets.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS tickets")
    c.execute("""CREATE TABLE tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, description TEXT, priority TEXT,
        category TEXT, status TEXT DEFAULT 'Open', created_at TEXT)""")
    now = datetime.now()
    data = [
        ("Password reset","User locked out after 3 attempts","High","Account Access","Open", (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")),
        ("Install Adobe Suite","Marketing needs Adobe on WS-204","Medium","Software","In Progress", (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")),
        ("VPN not connecting","Remote employee gets timeout error","High","Network","Open", (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")),
        ("New hire laptop setup","MacBook setup for new engineer","Medium","Hardware","In Progress", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),
        ("Printer jamming 3rd floor","HP LaserJet jams on duplex","Low","Hardware","Resolved", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")),
    ]
    c.executemany("INSERT INTO tickets (title,description,priority,category,status,created_at) VALUES (?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    print("Database initialized with 5 tickets.")

if __name__ == "__main__":
    init_db()
