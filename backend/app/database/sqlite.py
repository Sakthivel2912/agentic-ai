"""
AI Council - SQLite Database Connection
"""
import os
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

BACKEND_DIR = Path(__file__).resolve().parents[2]


def resolve_database_path(database: str | Path) -> Path:
    """Resolve relative SQLite paths from the backend directory, not the shell CWD."""
    path = Path(database).expanduser()
    if not path.is_absolute():
        path = BACKEND_DIR / path
    return path.resolve()


DATABASE_PATH = resolve_database_path(settings.SQLITE_DATABASE)

# Async engine for SQLite
async_engine = create_async_engine(
    URL.create("sqlite+aiosqlite", database=str(DATABASE_PATH)),
    echo=False,
    future=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sync engine for migrations
sync_engine = create_engine(
    URL.create("sqlite", database=str(DATABASE_PATH)),
    echo=False,
    future=True
)

# Sync session factory
SessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)


class SQLite:
    """SQLite database manager"""
    
    engine = None
    session_factory = None
    
    @classmethod
    async def connect_to_database(cls):
        """
        Create SQLite database connection
        """
        try:
            # Create all tables
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            upgrade_sqlite_schema(str(DATABASE_PATH))
            
            logger.info(f"Connected to SQLite: {DATABASE_PATH}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    @classmethod
    async def close_database_connection(cls):
        """
        Close SQLite database connection
        """
        await async_engine.dispose()
        logger.info("Closed SQLite connection")
    
    @classmethod
    def get_session(cls):
        """
        Get a managed async database session.

        This returns a real AsyncSession instance so callers can use either
        `session = sqlite.get_session()` followed by `await session.close()`
        or `async with sqlite.get_session() as session:`.
        """
        return AsyncSessionLocal()
    
    @classmethod
    def get_sync_session(cls):
        """
        Get sync database session
        """
        return SessionLocal()


# Global database instance
sqlite = SQLite()


def upgrade_sqlite_schema(db_path: str | None = None) -> None:
    """Add missing columns to existing SQLite research session tables."""
    target_db = os.path.abspath(db_path or DATABASE_PATH)
    conn = sqlite3.connect(target_db)
    try:
        table_info = conn.execute("PRAGMA table_info(research_sessions)").fetchall()
        if not table_info:
            return

        existing_columns = {row[1] for row in table_info}
        column_definitions = {
            "selected_agents": "TEXT NOT NULL DEFAULT '[]'",
            "selected_document_ids": "TEXT NOT NULL DEFAULT '[]'",
            "agent_outputs": "TEXT NOT NULL DEFAULT '{}'",
            "reviewer_feedback": "TEXT DEFAULT '{}'",
            "sources": "TEXT NOT NULL DEFAULT '[]'",
            "session_metadata": "TEXT NOT NULL DEFAULT '{}'",
            "error_message": "TEXT",
        }

        for column_name, column_sql in column_definitions.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE research_sessions ADD COLUMN {column_name} {column_sql}"
                )

        conn.commit()
    finally:
        conn.close()


