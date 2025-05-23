class TenantMaxSnapshotsDailyLimitReached(Exception):
    _date: str

    def __init__(
        self,
        /,
        date: str,
    ):
        self._date = date
        super().__init__(f"Tenant max snapshots daily limit reached: {date}")

    def __iter__(self):
        yield "name", __class__.__name__
        yield "date", self._date
