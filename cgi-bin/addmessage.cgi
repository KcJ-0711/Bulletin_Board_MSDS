#!/usr/bin/env python3
print("Content-type: text/html; charset=utf-8\n")

import cgi
import cgitb
import html
from db import get_db

cgitb.enable()

form = cgi.FieldStorage()
reply_to_raw = form.getvalue("reply_to", "").strip()
reply_to = int(reply_to_raw) if reply_to_raw.isdigit() else None

error = ""
if form.getvalue("submit"):
    subject = form.getvalue("subject", "").strip()
    sender = form.getvalue("sender", "").strip()
    text = form.getvalue("text", "").strip()

    if not subject or not sender or not text:
        error = "Subject, sender, and text are all required."
    elif len(sender) > 15:
        error = "Sender must be 15 characters or fewer."
    else:
        conn = get_db()
        curs = conn.cursor()
        if reply_to is not None:
            curs.execute(
                "INSERT INTO messages (reply_to, sender, subject, text) VALUES (?, ?, ?, ?)",
                (reply_to, sender, subject, text),
            )
        else:
            curs.execute(
                "INSERT INTO messages (sender, subject, text) VALUES (?, ?, ?)",
                (sender, subject, text),
            )
        conn.commit()
        conn.close()
        print("<meta http-equiv='refresh' content='0;url=main.cgi'>")
        raise SystemExit

heading = f"Reply to Message #{reply_to}" if reply_to is not None else "Post New Message"
hidden_reply = f'<input type="hidden" name="reply_to" value="{reply_to}">' if reply_to is not None else ""

print(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{html.escape(heading)}</title>
</head>
<body>
    <h1>{html.escape(heading)}</h1>
    <p style="color:red;">{html.escape(error)}</p>
    <form method="post" action="addmessage.cgi">
        {hidden_reply}
        Subject:<br>
        <input type="text" name="subject" maxlength="100" size="50" required><br><br>
        Sender (max 15 chars):<br>
        <input type="text" name="sender" maxlength="15" required><br><br>
        Text:<br>
        <textarea name="text" rows="5" cols="45" required></textarea><br><br>
        <input type="submit" name="submit" value="Post">
    </form>
    <p><a href="main.cgi">Back to Bulletin Board</a></p>
</body>
</html>
""")