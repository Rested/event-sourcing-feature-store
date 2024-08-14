# Event Sourcing / Feature Store

code accompanying a blog on interaction between event sourcing and feature stores.

## Structure

```
fleet_admin/
    - the fastapi app serving 
```

## Getting started

### Installation

```bash
uv pip install -r requirements.in
```

### Testing

```bash
pytest
```

### Run the fleet admin

```bash
uvicorn fleet_admin.app:app --reload  
```