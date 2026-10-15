import sqlite3
conn = sqlite3.connect('fin_suraksha.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    cnt = cur.fetchone()[0]
    cur.execute(f'PRAGMA table_info("{t}")')
    cols = [(r[1], r[2], r[5]) for r in cur.fetchall()]
    print(f'\n{t}: {cnt} rows')
    for c in cols:
        print(f'  {c[0]} ({c[1]}) PK={c[2]}')
    cur.execute(f'PRAGMA foreign_key_list("{t}")')
    fks = cur.fetchall()
    for fk in fks:
        print(f'  FK: {fk}')
conn.close()
