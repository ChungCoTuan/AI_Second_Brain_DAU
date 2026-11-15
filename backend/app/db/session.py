from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Tu chua lai sequence cho cac bang co cot `id` ---
# Truong hop: DB duoc `pg_restore` chi voi `-t <table>` (chi tao bang, KHONG tao sequence)
# => cot `id` mat DEFAULT nextval(...) => moi INSERT ra NULL va API bao loi 500.
# Ham nay tao lai sequence + gan DEFAULT + dong bo gia tri hien tai cho moi bang.
SEQUENCE_TABLES = [
    "users",
    "documents",
    "obligations",
    "thresholds",
    "document_relations",
    "document_embeddings",
    "audit_trails",
    "chat_sessions",
    "chat_messages",
]


def ensure_sequences() -> None:
    """Tao/ghan lai sequence cho cac bang co cot `id`. Chay an toan nhieu lan."""
    with engine.begin() as conn:
        for table in SEQUENCE_TABLES:
            seq = f"{table}_id_seq"
            try:
                conn.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {seq}"))
                conn.execute(
                    text(
                        f"ALTER TABLE {table} ALTER COLUMN id "
                        f"SET DEFAULT nextval('{seq}'::regclass)"
                    )
                )
                conn.execute(
                    text(
                        f"SELECT setval('{seq}', GREATEST("
                        f"COALESCE((SELECT MAX(id) FROM {table}), 0), 1))"
                    )
                )
            except Exception as exc:  # noqa: BLE001 - bang chua ton tai thi bo qua
                print(f"[DB] Bo qua sequence cho bang '{table}': {exc}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
