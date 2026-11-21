#!/usr/bin/env python3
print("Content-type: text/html; charset=utf-8\n")

import cgi
import cgitb
import html
import sqlite3
from db import get_db

cgitb.enable()

form = cgi.FieldStorage()
msg_id_raw = form.getvalue("id", "").strip()

if not msg_id_raw.isdigit():
    print("<p>Invalid message ID. <a href='main.cgi'>Back</a></p>")
    raise SystemExit

msg_id = int(msg_id_raw)
conn = get_db()
curs = conn.cursor()

error = ""
if form.getvalue("submit"):
    entered_sender = form.getvalue("sender", "").strip()

    curs.execute("SELECT sender FROM messages WHERE id = ?", (msg_id,))
    existing = curs.fetchone()

    if not existing:
        error = "Message not found."
    elif existing["sender"] != entered_sender:
        error = "Sender name does not match the original author."
    else:
        try:
            curs.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
            conn.commit()
            conn.close()
            print("<meta http-equiv='refresh' content='0;url=main.cgi'>")
            raise SystemExit
        except sqlite3.IntegrityError:
            error = "Cannot delete this message while other messages reply to it."

conn.close()

print(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Delete Message #{msg_id}</title>
</head>
<body>
    <h1>Delete Message #{msg_id}</h1>
    <p style="color:red;">{html.escape(error)}</p>
    <p>Enter your sender name to confirm deletion:</p>
    <form method="post" action="delete.cgi?id={msg_id}">
        Sender Name: <input type="text" name="sender" maxlength="15" required>
        <input type="submit" name="submit" value="Delete">
    </form>
    <p><a href="main.cgi">Back to Bulletin Board</a></p>
</body>
</html>
""")