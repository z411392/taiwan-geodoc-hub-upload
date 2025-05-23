from enum import Enum


class Bff(str, Enum):
    Assets = "assets"

    def __str__(self):
        return self.value
