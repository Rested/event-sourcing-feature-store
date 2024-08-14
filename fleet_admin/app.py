from fastapi.templating import Jinja2Templates
from event_store import EventStoreClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import uvicorn
from human_id import generate_id

from fleet_admin.read_model import FleetReadModel
from fleet_admin.command_handler import FleetCommandHandler
from starlette.concurrency import run_in_threadpool


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Event Store Client
event_store_client = EventStoreClient()
event_store_client.init_db()

event_store_client.get_events("asdas")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/fleet")
def create_fleet():
    return RedirectResponse(f"/fleet/{generate_id()}", status_code=303)


@app.get("/fleet/{aggregate_id}")
def get_fleet_status(aggregate_id: str, request: Request):
    raw_events = event_store_client.get_events(aggregate_id)
    # on demand for simplicity
    taxi_read_model = FleetReadModel()

    for raw_event in raw_events:
        taxi_read_model.apply_event(raw_event)

    fleet_status = taxi_read_model.get_fleet_status()
    return templates.TemplateResponse(
        "fleet_admin.html",
        {
            "request": request,
            "fleet_status": fleet_status,
            "aggregate_id": aggregate_id,
        },
    )


@app.post("/events/{aggregate_id}/{event_type}")
async def record_event(aggregate_id: str, event_type: str,  request: Request):
    event = await request.form()

    if not event:
        raise HTTPException(status_code=400, detail="Event data is required.")

    try:
        await run_in_threadpool(FleetCommandHandler(event_store_client).handle, 
            aggregate_id=aggregate_id,
            event_type=event_type,
            event=event
        )
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Unknown event type {event_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return await run_in_threadpool(get_fleet_status, aggregate_id=aggregate_id, request=request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
