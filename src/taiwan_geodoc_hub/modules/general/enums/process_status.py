from enum import Enum


class ProcessStatus(Enum):
    Pending = "pending"
    Progressing = "progressing"
    Completed = "completed"
    Failed = "failed"

    def __str__(self):
        return f"{self.value}"
