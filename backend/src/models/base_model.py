from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from flask import current_app
import os


Base = declarative_base()


def init_db(base):
    db_path = current_app.config.get("DB_PATH", f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/wsp.db'))}")
    engine = create_engine(db_path)
    base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    current_app.config["SESSION_LOCAL"] = SessionLocal