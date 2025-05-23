class TenantMaxSnapshotsDailyLimitReached(Exception):
    _date: str

    def __init__(
        self,
        /,
        date: str,
    ):
        self._date = date

    def __iter__(self):
        yield "name", __class__.__name__
        yield "date", self._date
