import sqlite3
from pathlib import Path
import time


DB_PATH = Path(__file__).resolve().parents[2] / 'runs' / '.runs_status.db'


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, status TEXT, results_path TEXT, updated_at INTEGER)"
    )
    conn.commit()
    return conn


def set_status(run_id: str, status: str, results_path: str | None = None):
    conn = _get_conn()
    now = int(time.time())
    conn.execute(
        "INSERT OR REPLACE INTO runs (run_id, status, results_path, updated_at) VALUES (?, ?, ?, ?)",
        (run_id, status, results_path, now),
    )
    conn.commit()
    conn.close()


def get_status(run_id: str):
    conn = _get_conn()
    cur = conn.execute("SELECT status, results_path, updated_at FROM runs WHERE run_id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {'status': row[0], 'results_path': row[1], 'updated_at': row[2]}
