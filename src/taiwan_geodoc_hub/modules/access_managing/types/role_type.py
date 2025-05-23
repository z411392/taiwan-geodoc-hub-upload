from enum import Enum


class RoleType(str, Enum):
    manager = "manager"
    member = "member"

    def __str__(self):
        return self.value
