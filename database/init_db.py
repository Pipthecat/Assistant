from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from config import DATABASE_URL, engine, Base

def create_database(database_url=DATABASE_URL):
    url = make_url(database_url)
    default_url = url.set(database="postgres")
    engine_default = create_engine(default_url, isolation_level="AUTOCOMMIT")

    with engine_default.connect() as conn:
        conn.execute(text(f"CREATE DATABASE {url.database}"))
        print(f"Database '{url.database}' created successfully!")

def init_db():
    # Create tables based on your ORM models
    Base.metadata.create_all(bind=engine)
    print("Tables initialized.")

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"Database might already exist. Skipping creation. ({e})")

    init_db()
