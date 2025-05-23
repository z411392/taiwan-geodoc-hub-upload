from base62 import decodebytes, encodebytes
from cloudevents.conversion import from_json
from cloudevents.http import CloudEvent


def destructure_ce(base62_encoded: str):
    json = decodebytes(base62_encoded)
    event = from_json(CloudEvent, json.decode("utf-8"))
    event_id: str = event.get("id")
    trace_id = encodebytes(event_id.encode("utf-8"))
    return trace_id, event.data
