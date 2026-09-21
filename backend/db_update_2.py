import sqlite3

try:
    conn = sqlite3.connect('e:/AI_Second_Brain_DAU/backend/sql_app.db')
    conn.execute("ALTER TABLE documents ADD COLUMN linh_vuc VARCHAR DEFAULT 'Giáo dục'")
    conn.commit()
    conn.close()
    print("Column linh_vuc added successfully.")
except sqlite3.OperationalError as e:
    print(f"Error (maybe column already exists): {e}")
