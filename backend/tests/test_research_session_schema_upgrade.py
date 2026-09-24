import sqlite3

from app.database.sqlite import upgrade_sqlite_schema


def test_upgrade_sqlite_schema_adds_missing_research_columns(tmp_path):
    db_path = tmp_path / "research-upgrade.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE research_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            question TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            status TEXT,
            progress REAL,
            current_stage TEXT,
            enable_rag INTEGER,
            enable_review INTEGER,
            enable_citations INTEGER,
            agent_outputs TEXT,
            reviewer_feedback TEXT,
            final_answer TEXT,
            sources TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            started_at DATETIME,
            completed_at DATETIME
        )
        """
    )
    conn.commit()
    conn.close()

    upgrade_sqlite_schema(str(db_path))

    conn = sqlite3.connect(str(db_path))
    columns = [row[1] for row in conn.execute("PRAGMA table_info(research_sessions)")]
    conn.close()

    assert "selected_document_ids" in columns
    assert "selected_agents" in columns
    assert "session_metadata" in columns
    assert "error_message" in columns
