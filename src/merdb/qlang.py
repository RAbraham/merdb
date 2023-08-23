from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Union
import re
from typing import List

@dataclass
class TimeStamp:
    nanoseconds: int = None
    datetime_value: datetime = None

    def __post_init__(self):
        if self.datetime_value is not None and self.nanoseconds is None:
            self.datetime = self.datetime_value
        elif self.nanoseconds is not None and self.datetime_value is None:
            pass
        else:
            raise ValueError("Either nanoseconds or datetime_value should be provided")

    @property
    def datetime(self) -> datetime:
        base_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        delta = timedelta(microseconds=round(self.nanoseconds / 1000))
        return base_date + delta

    @datetime.setter
    def datetime(self, value: datetime) -> None:
        base_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
        self.nanoseconds = int((value - base_date).total_seconds() * 1e9)

    @classmethod
    def from_string(cls, q_timestamp: str) -> Union['TimeStamp', None]:
        match = re.match(
            r'(\d{4}).(\d{2}).(\d{2})D(\d{2}):(\d{2}):(\d{2}).(\d{3})',
            q_timestamp
        )
        if not match:
            raise ValueError('Invalid timestamp format')
        year, month, day, hour, minute, second, millis = map(int, match.groups())
        value = datetime(
            year, month, day, hour, minute, second,
            millis * 1000, tzinfo=timezone.utc
        )
        instance = cls(datetime_value=value)
        return instance
def t(value: Union[str, int]) -> TimeStamp:
    if isinstance(value, str):
        return TimeStamp.from_string(value)
    elif isinstance(value, int):
        return TimeStamp(nanoseconds=value)
    else:
        raise TypeError("Invalid type. Expected str or int.")



def eq(s: str, c: str) -> List[int]:
    """Return a list of integers indicating if each character in `s` is equal to `c`."""
    return [int(char == c) for char in s]
