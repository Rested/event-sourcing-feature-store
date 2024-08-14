from datetime import datetime
import sqlite3
import json


sqlite3.register_adapter(datetime, lambda x: x.isoformat())
sqlite3.register_converter("datetime", lambda x: datetime.fromisoformat(x))


class EventStoreNotInitialized(Exception):
    """raised when an attempt is made to interact with the event store before it is initialized"""


class EventStoreClient:
    def __init__(self, db_name="events.db"):
        self.db_name = db_name
        self.initialized = False

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create the events table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aggregate_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        self.initialized = True

    def record_event(
        self, aggregate_id: str, event_type: str, event_data: str, created_at: datetime
    ):
        if not self.initialized:
            raise EventStoreNotInitialized(
                "Database not initialized. Call init_db() first."
            )

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO events (aggregate_id, event_type, event_data, created_at)
            VALUES (?, ?, ?, ?)
        """,
            (aggregate_id, event_type, event_data, created_at),
        )

        conn.commit()
        conn.close()

    def get_events(self, aggregate_id):
        if not self.initialized:
            raise EventStoreNotInitialized(
                "Database not initialized. Call init_db() first."
            )

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, aggregate_id, event_type, event_data, created_at
            FROM events
            WHERE aggregate_id = ?
            ORDER BY created_at
        """,
            (aggregate_id,),
        )

        events = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "aggregate_id": row[1],
                "event_type": row[2],
                "event_data": json.loads(row[3]),
                "created_at": row[4],
            }
            for row in events
        ]
