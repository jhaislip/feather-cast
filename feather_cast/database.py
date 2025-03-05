import sqlite3
from datetime import datetime, timedelta, timezone

DB_FILE = "detections.db"


def init_db():
    """Initialize the SQLite database and create tables if they don’t exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL,
            scientific_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            label TEXT NOT NULL,
            file_path TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def add_detection(detection):
    """Insert a detected bird into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO detections (common_name, scientific_name, confidence, label, file_path, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            detection["common_name"],
            detection["scientific_name"],
            detection["confidence"],
            detection["label"],
            detection["file_path"],
            detection["start_time"],
            detection["end_time"],
        ),
    )

    conn.commit()
    conn.close()


def get_recent_detections(limit=5, min_confidence=0.25):
    """Retrieve the most recent detection for each bird species within the last 24 hours."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Calculate time threshold (24 hours ago)
    time_threshold = (datetime.now() - timedelta(days=1)).isoformat()

    cursor.execute(
    """
        SELECT common_name, scientific_name, confidence, label, file_path, start_time, end_time, timestamp
        FROM detections
        WHERE timestamp >= ? AND confidence >= ?
        AND timestamp = (
            SELECT MAX(timestamp) 
            FROM detections AS d2 
            WHERE d2.common_name = detections.common_name
        )
        ORDER BY timestamp DESC
        LIMIT ?
    """,
        (time_threshold, min_confidence, limit),
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize database on import
init_db()
