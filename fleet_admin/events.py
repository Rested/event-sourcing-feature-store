from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime, UTC


class Event(BaseModel):
    created_at: datetime = Field(..., default_factory=lambda: datetime.now(UTC))


class TaxiAddedToFleet(Event):
    taxi_id: str
    license_plate: str
    model: str


class DriverJoinedFleet(Event):
    driver_id: str
    years_experience: int
    name: str

class DriverAssignedTaxi(Event):
    taxi_id: str
    driver_id: str

class DriverUnassignedTaxi(Event):
    taxi_id: str
    driver_id: str


class TaxiSentForMaintenance(Event):
    taxi_id: str


class TaxiReturnedFromMaintenance(Event):
    taxi_id: str


class TaxiBrokeDown(Event):
    taxi_id: str
    details: str


event_type_to_model: dict[str, Type[Event]] = {
    "DriverJoinedFleet": DriverJoinedFleet,
    "TaxiAddedToFleet": TaxiAddedToFleet,
    "DriverAssignedTaxi": DriverAssignedTaxi,
    "DriverUnassignedTaxi": DriverUnassignedTaxi,
    "TaxiSentForMaintenance": TaxiSentForMaintenance,
    "TaxiReturnedFromMaintenance": TaxiReturnedFromMaintenance,
    "TaxiBrokeDown": TaxiBrokeDown,
}
