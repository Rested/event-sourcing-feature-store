from fleet_admin.events import event_type_to_model, DriverAssignedTaxi
from event_store import EventStoreClient
from fleet_admin.read_model import FleetReadModel


class FleetCommandHandler:
    """we don't do any command seperation here for simplicity but still implement some minimal command validation"""
    def __init__(self, event_store_client: EventStoreClient):
        self.event_store_client = event_store_client

    def handle(self, aggregate_id: str, event_type: str, event: dict):
        raw_events = self.event_store_client.get_events(aggregate_id)
        taxi_read_model = FleetReadModel()
        
        for raw_event in raw_events:
            taxi_read_model.apply_event(raw_event)

    
        event_model = event_type_to_model[event_type](**event)

        match event_model:
            case DriverAssignedTaxi():
                if not taxi_read_model.can_assign_driver_to_taxi(event_model.driver_id, event_model.taxi_id):
                    raise ValueError("Cannot assign driver to taxi: Taxi is either occupied or in maintenance.")


        self.event_store_client.record_event(
            aggregate_id,
            event_type,
            event_model.model_dump_json(exclude={"created_at"}),
            event_model.created_at,
        )

