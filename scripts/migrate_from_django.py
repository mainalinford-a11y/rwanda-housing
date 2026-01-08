"""
Simple migration script: export selected data from Django's sqlite3 `db.sqlite3`
and import into the new FastAPI/SQLModel SQLite database `rwanda.db`.

This script migrates users and properties with minimal fields.
Run locally: `python scripts/migrate_from_django.py`
"""
import sqlite3
import os
import shutil
from sqlmodel import Session, create_engine
from api.app import User, Property, SQLModel

DJANGO_DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
TARGET_DB = os.path.join(os.path.dirname(__file__), '..', 'rwanda.db')

def migrate():
    # Ensure target DB exists and tables are created by importing app and calling create_db_and_tables
    from api.app import create_db_and_tables
    create_db_and_tables()

    conn = sqlite3.connect(DJANGO_DB)
    cur = conn.cursor()

    with Session(create_engine(f"sqlite:///{TARGET_DB}")) as session:
        # Migrate users (basic fields: username, email)
        try:
            cur.execute("SELECT id, username, email FROM auth_user")
            rows = cur.fetchall()
        except sqlite3.Error:
            rows = []

        for r in rows:
            uid, username, email = r
            existing = session.exec(SQLModel.select(User).where(User.username == username)).first()
            if existing:
                continue
            user = User(username=username, email=email)
            session.add(user)

        session.commit()

        # Migrate properties if a table exists
        try:
            cur.execute("SELECT id, title, location, price, description FROM housing_property")
            props = cur.fetchall()
        except sqlite3.Error:
            props = []

        for p in props:
            pid, title, location, price, description = p
            prop = Property(title=title or 'Untitled', location=location, price=price or 0, description=description or '')
            session.add(prop)

        session.commit()

    conn.close()

if __name__ == '__main__':
    migrate()
    print('Migration completed (users and properties).')
