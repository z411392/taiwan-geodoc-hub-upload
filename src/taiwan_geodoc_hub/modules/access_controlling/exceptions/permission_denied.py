class PermissionDenied(Exception):
    def __init__(self):
        super().__init__("Permission denied")

    def __iter__(self):
        yield "name", __class__.__name__
