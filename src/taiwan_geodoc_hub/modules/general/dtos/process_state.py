from taiwan_geodoc_hub.modules.general.enums.process_status import (
    ProcessStatus,
)
from typing import Union, TypedDict, Literal


class ProcessStateBase(TypedDict):
    id: str


class Pending(ProcessStateBase):
    status: Literal[ProcessStatus.Pending]


class Progressing(ProcessStateBase):
    status: Literal[ProcessStatus.Progressing]


class Completed(ProcessStateBase):
    status: Literal[ProcessStatus.Completed]


class Failed(ProcessStateBase):
    status: Literal[ProcessStatus.Failed]
    reason: str


ProcessState = Union[Pending, Progressing, Completed, Failed]
