class InvalidPDF(Exception):
    def __init__(self):
        super().__init__("Invalid PDF")

    def __iter__(self):
        yield "name", __class__.__name__
