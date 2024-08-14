
from pydantic import ValidationError
from fleet_admin.events import (
    Event,
    DriverJoinedFleet,
    DriverUnassignedTaxi,
    DriverAssignedTaxi,
    TaxiAddedToFleet,
    TaxiBrokeDown,
    TaxiReturnedFromMaintenance,
    TaxiSentForMaintenance,
    event_type_to_model,
)



class FleetReadModel:
    def __init__(self):
        self.taxis: dict[str, dict] = {}
        self.drivers: dict[str, str] = {}

    def apply_event(self, event: dict):
        event_type = event["event_type"]
        event_data = event["event_data"]
        created_at = event["created_at"]

        if event_type in event_type_to_model:
            EventModel = event_type_to_model[event_type]

            try:
                # Instantiate the Pydantic model
                event_instance = EventModel(**event_data, created_at=created_at)
                # Handle the event using the instantiated model
                self.handle_event(event_instance)
            except ValidationError as e:
                print(f"Failed to validate event data for type {event_type}: {e}")
        else:
            print(f"Unknown event type: {event_type}")

    def handle_event(self, event: Event):
        match event:
            case TaxiAddedToFleet():
                self.add_taxi(event)
            case DriverJoinedFleet():
                self.add_driver(event)
            case DriverAssignedTaxi():
                self.assign_driver_to_taxi(event)
            case DriverUnassignedTaxi():
                self.unassign_driver_from_taxi(event)
            case TaxiSentForMaintenance():
                self.update_taxi_status(event, "In Maintenance")
            case TaxiReturnedFromMaintenance():
                self.update_taxi_status(event, "Available")
            case TaxiBrokeDown():
                self.update_taxi_status(event, "Broken Down")

    def add_taxi(self, event: TaxiAddedToFleet):
        self.taxis[event.taxi_id] = {
            "license_plate": event.license_plate,
            "model": event.model,
            "status": "Available",
            "driver_id": None,
        }

    def add_driver(self, event: DriverJoinedFleet):
        self.drivers[event.driver_id] = {
            "name": event.name,
            "taxi_id": None,
        }

    def can_assign_driver_to_taxi(self, driver_id: str, taxi_id: str) -> bool:
        taxi = self.taxis.get(taxi_id)
        driver = self.drivers.get(driver_id)
        
        if not taxi or not driver:
            return False
        
        # Check if the taxi is available and not assigned or in maintenance
        if taxi["status"] == "Available" and taxi["driver_id"] is None:
            return True
        return False


    def assign_driver_to_taxi(self, event: DriverAssignedTaxi):
        if event.taxi_id in self.taxis:
            self.taxis[event.taxi_id]["driver_id"] = event.driver_id
            self.drivers[event.driver_id]["taxi_id"] = event.taxi_id

    def unassign_driver_from_taxi(self, event: DriverUnassignedTaxi):
        if event.taxi_id in self.taxis:
            self.taxis[event.taxi_id]["driver_id"] = None

    def update_taxi_status(
        self,
        event: TaxiSentForMaintenance | TaxiReturnedFromMaintenance | TaxiBrokeDown,
        status: str,
    ):
        if event.taxi_id in self.taxis:
            self.taxis[event.taxi_id]["status"] = status

    def get_fleet_status(self):
        return {
            "taxis": self.taxis,
            "drivers": self.drivers,
        }