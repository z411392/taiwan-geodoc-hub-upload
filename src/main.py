if __name__ == "__main__":
    from dotenv import load_dotenv
    from os.path import exists
    from os import environ
    from taiwan_geodoc_hub.entrypoints.cli import typer

    environ["RUN_MODE"] = "cli"

    if exists("src/.env"):
        load_dotenv("src/.env", override=True)

    if exists("src/.env.local"):
        load_dotenv("src/.env.local", override=True)

    typer()

else:
    from taiwan_geodoc_hub.entrypoints.http.assets import assets  # noqa: F401
