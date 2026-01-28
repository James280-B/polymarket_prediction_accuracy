import pytz

from datetime import datetime, timezone


class PolyUtilsHandler(object):

    @staticmethod
    def cast_poly_to_datetime(date: str) -> datetime:
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def cast_utc_to_datetime(date: float) -> datetime:
        dt = datetime.fromtimestamp(date, tz=timezone.utc)
        return dt

    @staticmethod
    def cast_poly_to_utc(date: str) -> datetime:
        date_dt = datetime.fromisoformat(date)
        dt_utc = date_dt.astimezone(pytz.utc)
        return dt_utc
