#!/usr/bin/env python3
print("Content-type: text/html; charset=utf-8\n")

import cgi
import cgitb
import html
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
    new_subject = form.getvalue("subject", "").strip()
    new_text = form.getvalue("text", "").strip()

    curs.execute("SELECT sender FROM messages WHERE id = ?", (msg_id,))
    existing = curs.fetchone()

    if not existing:
        error = "Message not found."
    elif existing["sender"] != entered_sender:
        error = "Sender name does not match the original author."
    elif not new_subject or not new_text:
        error = "Subject and text cannot be empty."
    else:
        curs.execute(
            "UPDATE messages SET subject = ?, text = ? WHERE id = ?",
            (new_subject, new_text, msg_id),
        )
        conn.commit()
        conn.close()
        print("<meta http-equiv='refresh' content='0;url=main.cgi'>")
        raise SystemExit

curs.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
message = curs.fetchone()
conn.close()

if not message:
    print("<p>Message not found. <a href='main.cgi'>Back</a></p>")
    raise SystemExit

print(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Edit Message #{msg_id}</title>
</head>
<body>
    <h1>Edit Message #{msg_id}</h1>
    <p style="color:red;">{html.escape(error)}</p>
    <form method="post" action="edit.cgi?id={msg_id}">
        Your Sender Name (for ownership check):<br>
        <input type="text" name="sender" maxlength="15" required><br><br>
        Subject:<br>
        <input type="text" name="subject" maxlength="100" size="50" value="{html.escape(message['subject'])}" required><br><br>
        Text:<br>
        <textarea name="text" rows="5" cols="45" required>{html.escape(message['text'])}</textarea><br><br>
        <input type="submit" name="submit" value="Save Changes">
    </form>
    <p><a href="main.cgi">Back to Bulletin Board</a></p>
</body>
</html>
""")