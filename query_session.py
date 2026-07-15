"""Query MiMoCode session parts from the local SQLite database.

Usage:
    python query_session.py                  # compact summary
    python query_session.py --full           # detailed output (800/600/500 char limits)
    python query_session.py --session ID     # query a specific session
"""
import sqlite3
import json
import sys

DB_PATH = r'C:\Users\FoxVuk\.local\share\mimocode\mimocode.db'
DEFAULT_SESSION = 'ses_09a786cd8ffe73o7wrHf280dhV'


def query(session_id: str, full: bool = False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'SELECT id, data FROM part WHERE session_id = ? ORDER BY time_created',
        (session_id,),
    )
    rows = cur.fetchall()
    conn.close()

    label = "FULL" if full else "COMPACT"
    print(f'=== {len(rows)} parts in {session_id} ({label}) ===')

    text_limit = 800 if full else 500
    inp_limit = 600 if full else 300
    out_limit = 600 if full else 300

    for r in rows:
        d = json.loads(r[1])
        t = d.get('type', '?')

        if t == 'text':
            text = (d.get('text', '') or '')[:text_limit]
            print(f'\n--- TEXT ---')
            print(text)
        elif t == 'tool':
            tool = d.get('tool', '?')
            state = d.get('state', {})
            inp = json.dumps(state.get('input', ''), ensure_ascii=False)[:inp_limit]
            out = str(state.get('output', ''))[:out_limit]
            if full:
                print(f'\n--- TOOL: {tool} ---')
                print(f'INPUT: {inp}')
                print(f'OUTPUT: {out}')
            else:
                print(f'  {r[0]}: TOOL={tool}: INPUT={inp} OUTPUT={out}')
        elif t == 'reasoning':
            text = (d.get('text', '') or '')[:500]
            print(f'\n--- REASONING ---')
            print(text)
        elif t == 'step-start':
            if full:
                print(f'\n--- STEP-START ---')
            else:
                print(f'  {r[0]}: STEP-START')
        elif t == 'step-finish':
            tokens = d.get('tokens', {})
            if full:
                print(f'\n--- STEP-FINISH tokens={tokens} ---')
            else:
                print(f'  {r[0]}: STEP-FINISH tokens={tokens}')
        else:
            if full:
                print(f'\n--- {t} ---')
            else:
                print(f'  {r[0]}: {t}')


if __name__ == '__main__':
    full = '--full' in sys.argv
    session = DEFAULT_SESSION
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--session' and i < len(sys.argv) - 1:
            session = sys.argv[i + 1]
    query(session, full)
