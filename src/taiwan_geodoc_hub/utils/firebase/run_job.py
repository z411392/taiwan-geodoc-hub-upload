from google.cloud.run_v2 import JobsClient
from google.cloud.run_v2 import RunJobRequest
from google.cloud.run_v2 import EnvVar
from os import getenv
from typing import Optional, Dict
from taiwan_geodoc_hub.utils.firebase.credentials_from_env import (
    credentials_from_env,
)

jobs_client: Optional[JobsClient] = None


def run_job(
    job_name: str,
    /,
    args: Optional[list[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    location: Optional[str] = None,
):
    if location is None:
        location = "asia-east1"

    container_override = None
    if env_vars or args:
        container_override = RunJobRequest.Overrides.ContainerOverride()

        if env_vars:
            container_override.env.extend(
                [EnvVar(name=key, value=value) for key, value in env_vars.items()]
            )

        if args:
            container_override.args.extend(args)

    overrides = None
    if container_override:
        overrides = RunJobRequest.Overrides()
        overrides.container_overrides = [container_override]

    global jobs_client
    if jobs_client is None:
        jobs_client = JobsClient(credentials=credentials_from_env())

    name = f"projects/{getenv('PROJECT_ID')}/locations/{location}/jobs/{job_name}"
    operation = jobs_client.run_job(
        request=RunJobRequest(
            name=name,
            overrides=overrides,
        )
    )
    return operation
