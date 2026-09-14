import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import DocumentRelation

DATABASE_URL = "postgresql://postgres:123456789@localhost:5432/dau_second_brain"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_relation_data():
    db = SessionLocal()
    try:
        # Create relation: TT 08/2021 bị thay thế bởi TT 17/2021
        r1 = DocumentRelation(source_doc="TT 08/2021/TT-BGDĐT", target_doc="TT 17/2021/TT-BGDĐT", relation_type="bị thay thế")
        
        # Create dependents (Căn cứ vào TT 08/2021)
        r2 = DocumentRelation(source_doc="QĐ 324/QĐ-ĐHKTĐN", target_doc="TT 08/2021/TT-BGDĐT", relation_type="căn cứ")
        r3 = DocumentRelation(source_doc="QĐ 104/QĐ-ĐHKTĐN", target_doc="TT 08/2021/TT-BGDĐT", relation_type="căn cứ")

        db.add(r1)
        db.add(r2)
        db.add(r3)
        db.commit()
        print("Seeded DocumentRelation data successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_relation_data()
