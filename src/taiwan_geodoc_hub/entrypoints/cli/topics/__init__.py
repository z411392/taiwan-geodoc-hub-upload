from typer import Typer
from taiwan_geodoc_hub.modules.general.presentation.cli.handlers.handle_init_topics import (
    handle_init_topics,
)

topics = Typer(name="topics")
topics.command(name="init")(handle_init_topics)
