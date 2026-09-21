from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as con:
        con.execute(text("ALTER TABLE documents ADD COLUMN linh_vuc VARCHAR DEFAULT 'Giáo dục'"))
        con.commit()
        print("Successfully added column linh_vuc")
except Exception as e:
    print("Error:", e)
