if __name__ == "__main__":
    from dotenv import load_dotenv
    from os.path import exists
    from os import environ
    from taiwan_geodoc_hub.entrypoints.cli.typer import app

    environ["RUN_MODE"] = "cli"

    if exists("src/.env"):
        load_dotenv("src/.env", override=True)
    if exists("src/.env.local"):
        load_dotenv("src/.env.local", override=True)
    app()

else:
    from firebase_functions.https_fn import on_request
    from werkzeug.wrappers import Request
    from vellox import Vellox
    from taiwan_geodoc_hub.entrypoints.http.starlette import app
    from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop

    vellox = Vellox(
        app=app,
    )

    @on_request()
    def upload(request: Request):
        loop = ensure_event_loop()
        return loop.run_until_complete(vellox(request))

    from firebase_functions.pubsub_fn import (
        on_message_published,
        CloudEvent,
        MessagePublishedData,
    )
    from taiwan_geodoc_hub.modules.system_maintaining.types.topic import Topic
    from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_uploaded import (
        SnapshotUploaded,
    )
    from taiwan_geodoc_hub.utils.firebase.run_job import run_job

    @on_message_published(topic=str(Topic.SnapshotUploaded))
    def on_snapshot_uploaded(
        event: CloudEvent[MessagePublishedData[SnapshotUploaded]],
    ):
        return run_job("worker", args=["help"])
