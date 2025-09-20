"""Simple CLI to query run status from the SQLite DB.

Usage:
  python tools/orchestrate/status_cli.py [run_id]
If run_id is omitted, prints all runs.
"""
import argparse
from tools.orchestrate import status_db
import time


def format_row(run_id, info):
    updated = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(info['updated_at'])) if info.get('updated_at') else 'N/A'
    return f"{run_id}\t{info.get('status')}\t{info.get('results_path')}\t{updated}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument('run_id', nargs='?')
    args = p.parse_args()

    if args.run_id:
        info = status_db.get_status(args.run_id)
        if not info:
            print('run not found')
            return
        print(format_row(args.run_id, info))
    else:
        # list all runs
        # brute-force by reading DB directly via status_db._get_conn
        conn = status_db._get_conn()
        cur = conn.execute('SELECT run_id, status, results_path, updated_at FROM runs')
        rows = cur.fetchall()
        conn.close()
        print('run_id\tstatus\tresults_path\tupdated_at')
        for r in rows:
            print(format_row(r[0], {'status': r[1], 'results_path': r[2], 'updated_at': r[3]}))


if __name__ == '__main__':
    main()
