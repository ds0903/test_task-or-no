from contextlib import contextmanager
from app.core.db import SessionLocal


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"DB помилка через :( {e}")
        raise
    finally:
        db.close()

def get_db():
    with session_scope() as db:
        yield db
