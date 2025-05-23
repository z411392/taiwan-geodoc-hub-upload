from enum import Enum


class RegistrationType(str, Enum):
    building = "building"
    land = "land"

    def __str__(self):
        return self.value
