import os
from datetime import datetime
from sqlalchemy import (
    create_engine, text,
    Column, Integer, String, Text, DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    relationship, sessionmaker, declarative_base
)
from sqlalchemy.engine.url import make_url

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

# Create an engine for the target database (assuming it exists)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# ------------------------------------------------------------------
# ORM Models (based on the ER diagram)
# ------------------------------------------------------------------

class Role(Base):
    __tablename__ = "Roles"

    role_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    # Relationship to users
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey("Roles.role_id"))

    # Relationships
    role = relationship("Role", back_populates="users")
    tasks = relationship("Task", back_populates="assigned_user")
    logs = relationship("Log", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Project(Base):
    __tablename__ = "Projects"

    project_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # Relationships
    backlogs = relationship("Backlog", back_populates="project")
    resources = relationship("Resource", back_populates="project")
    tasks = relationship("Task", back_populates="project")


class Backlog(Base):
    __tablename__ = "Backlog"

    backlog_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("Projects.project_id"))
    name = Column(String(200), nullable=False)
    priority = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to Project
    project = relationship("Project", back_populates="backlogs")


class Resource(Base):
    __tablename__ = "Resources"

    resource_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("Projects.project_id"))
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=True)
    url = Column(String(300), nullable=True)

    # Relationship back to Project
    project = relationship("Project", back_populates="resources")


class Status(Base):
    __tablename__ = "Statuses"

    status_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Relationship to tasks
    tasks = relationship("Task", back_populates="status")


class Task(Base):
    __tablename__ = "Tasks"

    task_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("Projects.project_id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status_id = Column(Integer, ForeignKey("Statuses.status_id"))
    assigned_user_id = Column(Integer, ForeignKey("Users.user_id"))
    deadline = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    status = relationship("Status", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")
    logs = relationship("Log", back_populates="task")
    comments = relationship("Comment", back_populates="task")


class Log(Base):
    __tablename__ = "Logs"

    log_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("Tasks.task_id"))
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    change_description = Column(Text, nullable=True)
    change_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="logs")
    user = relationship("User", back_populates="logs")


class Comment(Base):
    __tablename__ = "Comments"

    comment_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("Tasks.task_id"))
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    content = Column(Text, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")

# ------------------------------------------------------------------
# Database existence & initialization helpers
# ------------------------------------------------------------------

def check_database_exists(database_url=DATABASE_URL):
    """
    Connect to the default 'postgres' database and check
    if the target database already exists in pg_database.
    """
    url = make_url(database_url)
    default_url = url.set(database="postgres")  # Switch to the default DB
    engine_default = create_engine(default_url)

    query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
    with engine_default.connect() as conn:
        result = conn.execute(query, {"dbname": url.database})
        return result.scalar() is not None


def create_database_if_not_exists(database_url=DATABASE_URL):
    """
    If the target database doesn't exist, create it.
    """
    if not check_database_exists(database_url):
        url = make_url(database_url)
        default_url = url.set(database="postgres")
        engine_default = create_engine(default_url)

        with engine_default.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {url.database}"))
            conn.commit()

        print(f"Database '{url.database}' created.")
    else:
        print(f"Database '{make_url(database_url).database}' already exists.")


def init_db():
    """
    1. Create the database if it does not exist.
    2. Create all tables (if not already present) based on the ORM schema.
    """
    create_database_if_not_exists(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created (if not already existing).")


# ------------------------------------------------------------------
# Run initialization if executed directly
# ------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
