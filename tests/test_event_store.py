from datetime import UTC, datetime
from pathlib import Path
from event_store import EventStoreClient, EventStoreNotInitialized
import pytest
import json


@pytest.fixture
def client(tmp_path: Path) -> EventStoreClient:
    return EventStoreClient(db_name=tmp_path / "events.db")


def test_cannot_interact_without_db_being_initialized(client: EventStoreClient):
    with pytest.raises(EventStoreNotInitialized):
        client.get_events("my-agg")

    with pytest.raises(EventStoreNotInitialized):
        client.record_event(
            "my-agg",
            "some-event",
            json.dumps({"some": "data"}),
            created_at=datetime.now(UTC),
        )


def test_can_record_and_retrieve_events(client: EventStoreClient):
    client.init_db()
    event_data = {"some": "data"}
    created_at = datetime.now(UTC)
    client.record_event(
        "my-agg",
        "some-event",
        json.dumps(event_data),
        created_at=created_at,
    )
    events = client.get_events("my-agg")
    assert events == [
        {
            "id": 1,
            "aggregate_id": "my-agg",
            "event_type": "some-event",
            "event_data": event_data,
            "created_at": created_at.isoformat(),
        }
    ]
