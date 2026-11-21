#!/usr/bin/env python3
print("Content-type: text/html; charset=utf-8\n")

import cgi
import cgitb
import html
from db import get_db

cgitb.enable()

form = cgi.FieldStorage()
search_subject = form.getvalue("subject", "").strip()
search_sender = form.getvalue("sender", "").strip()

conn = get_db()
curs = conn.cursor()

query = "SELECT * FROM messages WHERE 1=1"
params = []

if search_subject and search_sender:
    query += " AND subject LIKE ? AND sender LIKE ?"
    params.extend([f"%{search_subject}%", f"%{search_sender}%"])
elif search_subject:
    query += " AND subject LIKE ?"
    params.append(f"%{search_subject}%")
elif search_sender:
    query += " AND sender LIKE ?"
    params.append(f"%{search_sender}%")

query += " ORDER BY id ASC"

curs.execute(query, params)
rows = curs.fetchall()
conn.close()

toplevel = []
children = {}
row_ids = {row["id"] for row in rows}

for row in rows:
    parent_id = row["reply_to"]
    # When searching, show matching replies under their parent if present, or at top level if parent isn't in filtered results
    if parent_id is None or parent_id not in row_ids:
        toplevel.append(row)
    else:
        children.setdefault(parent_id, []).append(row)

esc_subject = html.escape(search_subject)
esc_sender = html.escape(search_sender)

print(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>The Bulletin Board - P1</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; background: #fafafa; color: #222; }}
        .msg {{ background: #fff; border: 1px solid #ccc; padding: 12px; margin-bottom: 10px; }}
        .meta {{ font-size: 0.85em; color: #555; margin-bottom: 6px; }}
        .thread {{ margin-left: 24px; border-left: 2px solid #bbb; padding-left: 12px; margin-top: 8px; }}
        form {{ background: #fff; border: 1px solid #ccc; padding: 12px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>The Bulletin Board</h1>
    <p><a href="addmessage.cgi">Post New Message</a></p>

    <form method="get" action="main.cgi">
        <strong>Search</strong><br><br>
        Subject: <input type="text" name="subject" value="{esc_subject}">
        Sender: <input type="text" name="sender" value="{esc_sender}">
        <input type="submit" value="Search">
        <a href="main.cgi">Reset</a>
    </form>
    <hr>
""")


def render_message(row):
    msg_id = row["id"]
    subj = html.escape(row["subject"])
    sender = html.escape(row["sender"])
    created_at = html.escape(str(row["created_at"]))
    body = html.escape(row["text"]).replace("\n", "<br>")

    print(f"""
    <div class="msg">
        <strong>{subj}</strong>
        <div class="meta">
            By <strong>{sender}</strong> | {created_at} |
            <a href="addmessage.cgi?reply_to={msg_id}">Reply</a> |
            <a href="edit.cgi?id={msg_id}">Edit</a> |
            <a href="delete.cgi?id={msg_id}">Delete</a>
        </div>
        <div>{body}</div>
    </div>
    """)

    if msg_id in children:
        print('<div class="thread">')
        for kid in children[msg_id]:
            render_message(kid)
        print("</div>")


if not toplevel:
    print("<p>No messages found.</p>")
else:
    for msg in toplevel:
        render_message(msg)

print("""
</body>
</html>
""")