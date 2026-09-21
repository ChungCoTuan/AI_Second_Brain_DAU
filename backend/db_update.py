import sqlite3
conn = sqlite3.connect('e:/AI_Second_Brain_DAU/backend/sql_app.db')
conn.execute("ALTER TABLE documents ADD COLUMN linh_vuc VARCHAR DEFAULT 'Giáo d?c'")
conn.commit()
conn.close()
