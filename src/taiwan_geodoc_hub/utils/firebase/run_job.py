from typing import Optional
from firebase_functions.pubsub_fn import (
    CloudEvent,
    MessagePublishedData,
)
from cloudevents.http import CloudEvent as CEHTTP
from cloudevents.conversion import to_json
from base62 import encodebytes
from taiwan_geodoc_hub.utils.environments import is_emulating
from subprocess import Popen, PIPE
from os import getenv
from taiwan_geodoc_hub.utils.firebase.credentials_from_env import (
    credentials_from_env,
)
from google.cloud.run_v2 import JobsClient
from google.cloud.run_v2 import RunJobRequest

jobs_client: Optional[JobsClient] = None


def run_job(
    *args,
    event: CloudEvent[MessagePublishedData],
):
    ce = encodebytes(
        to_json(
            CEHTTP(
                dict(
                    id=event.id,
                    source=event.source,
                    type=event.type,
                    specversion=event.specversion,
                ),
                event.data.message.json,
            )
        )
    )
    args = (*args, f"--ce={ce}")
    if is_emulating():
        process = Popen(["python", "main.py", *args], stdout=PIPE, text=True)
        for line in process.stdout:
            print(line, end="")
        if process.returncode == 0:
            return
        if process.stderr is None:
            return
        raise Exception(process.stderr)

    global jobs_client
    if jobs_client is None:
        jobs_client = JobsClient(credentials=credentials_from_env())

    job_name = "worker"
    location = "asia-east1"
    container_override = RunJobRequest.Overrides.ContainerOverride()
    container_override.args.extend(args)
    overrides = RunJobRequest.Overrides()
    overrides.container_overrides = [container_override]

    name = f"projects/{getenv('PROJECT_ID')}/locations/{location}/jobs/{job_name}"
    operation = jobs_client.run_job(
        request=RunJobRequest(
            name=name,
            overrides=overrides,
        )
    )
    return operation
