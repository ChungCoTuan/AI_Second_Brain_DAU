import sys
import os
sys.path.append('e:/AI_Second_Brain_DAU/backend')
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as con:
    try:
        con.execute(text('ALTER TABLE documents ADD COLUMN tom_tat TEXT;'))
        con.commit()
        print('Column added')
    except Exception as e:
        print(e)
