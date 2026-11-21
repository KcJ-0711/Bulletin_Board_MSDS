# Bulletin Board — Part 1 (CGI)

## Overview
Part 1 extends the lecture CGI bulletin board using SQLite (`sqlite3`) and Python DB-API 2.0 with:
- Automatic `created_at` timestamps (`DATETIME DEFAULT CURRENT_TIMESTAMP`) and display on the board.
- Search by `subject` and/or `sender` using `LIKE` (`AND` when both are provided).
- Editing and deleting messages after matching the entered `sender` name.

## Project Structure
```text
bulletin_board_p1/
├── requirements.txt
├── schema.sql
├── run_cgi.py
├── bulletin.db          # Generated automatically when initialized/run
├── README.md
└── cgi-bin/
    ├── db.py
    ├── main.cgi
    ├── addmessage.cgi
    ├── edit.cgi
    └── delete.cgi
```

### File Roles
- `requirements.txt` — Installs `legacy-cgi==2.6; python_version >= '3.13'` for Python 3.13+ environments where `cgi` and `cgitb` are no longer in the standard library.
- `schema.sql` — Defines the `messages` table with `id`, `subject`, `sender`, `reply_to`, `text`, and `created_at`.
- `run_cgi.py` — Small local HTTP/CGI server wrapper that routes `/cgi-bin/*.cgi` requests using the active Python interpreter (avoids Windows `WinError 193` when running `.cgi` scripts directly).
- `cgi-bin/db.py` — Opens SQLite connections (`bulletin.db`), enables foreign keys, configures dictionary-like row access (`sqlite3.Row`), and initializes the database from `schema.sql` if needed.
- `cgi-bin/main.cgi` — Renders threaded messages, timestamps, links to reply/edit/delete, and the subject/sender search form.
- `cgi-bin/addmessage.cgi` — Handles creating new top-level messages and replying to existing messages (`?reply_to=<id>`).
- `cgi-bin/edit.cgi` — Verifies sender ownership and updates message `subject` and `text`.
- `cgi-bin/delete.cgi` — Verifies sender ownership and deletes a message (`?id=<id>`).

## Setup & Execution (Windows + `.venv` + Python 3.13)

1. **Create and activate a virtual environment, then install dependencies:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Initialize the SQLite database (optional):**
   `cgi-bin/db.py` automatically creates `bulletin.db` using `schema.sql` when the app runs if `bulletin.db` does not exist yet. To initialize or reset it manually beforehand:
   ```powershell
   sqlite3 bulletin.db ".read schema.sql"
   ```
   *(If `sqlite3.exe` is not installed on your `PATH`, skip this step and let `run_cgi.py` / `db.py` initialize `bulletin.db` automatically.)*

3. **Start the CGI server:**
   Run `run_cgi.py` from the project root (`bulletin_board_p1`):
   ```powershell
   & ".\.venv\Scripts\python.exe" ".\run_cgi.py"
   ```

4. **Open in your browser:**
   Navigate to:
   ```text
   http://localhost:8000/cgi-bin/main.cgi
   ```
   From there, you can post messages, reply to threads, search by subject and/or sender, and edit or delete messages matching your sender name.