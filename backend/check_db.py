from app.db.session import engine
from sqlalchemy import text

with engine.connect() as con:
    res = con.execute(text("SELECT id, filename, status FROM documents")).fetchall()
    for r in res:
        print(r)
