from typing import TypedDict, Optional
from injector import Injector


class Context(TypedDict):
    injector: Optional[Injector]


context = Context(
    injector=None,
)
