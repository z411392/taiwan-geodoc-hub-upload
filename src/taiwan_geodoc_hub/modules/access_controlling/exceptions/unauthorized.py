class Unauthorized(Exception):
    def __init__(self):
        super().__init__("Unauthorized")

    def __iter__(self):
        yield "name", __class__.__name__
