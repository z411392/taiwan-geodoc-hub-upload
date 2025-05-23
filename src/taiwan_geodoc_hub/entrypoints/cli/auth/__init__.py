from typer import Typer
from taiwan_geodoc_hub.modules.access_controlling.presentation.cli.handlers.handle_login import (
    handle_login,
)

auth = Typer(name="auth")
auth.command(name="login")(handle_login)
