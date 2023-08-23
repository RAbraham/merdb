from hypothesis import given, strategies as st
from datetime import datetime, timezone
from merdb.qlang import TimeStamp, t, eq

# For Hypothesis to generate datetime objects
# dates = st.dates(min_value=datetime(2000, 1, 1), max_value=datetime(2099, 12, 31))
# times = st.times()


# For Hypothesis to generate datetime objects
datetimes = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2099, 12, 31),
    timezones=st.just(timezone.utc)
# )
).map(lambda dt: dt.replace(microsecond=(dt.microsecond // 1000) * 1000))
# ).map(lambda dt: dt.replace(microsecond=(dt.microsecond // 1000) * 1000))

@given(datetimes)
def test_timestamp_from_datetime(datetime_value: datetime):
    timestamp = TimeStamp(datetime_value=datetime_value)
    assert timestamp.datetime == datetime_value


# Define strategies to generate each part of the date/time
years = st.integers(2000, 2099)
months = st.integers(1, 12)
days = st.integers(1, 28)  # this works for all months
february_days = st.integers(1, 29)  # this is only for February in a leap year
hours = st.integers(0, 23)
minutes = st.integers(0, 59)
seconds = st.integers(0, 59)
milliseconds = st.integers(0, 999)

# Define strategy to generate a leap year
leap_years = st.integers(2000, 2096).filter(lambda x: x % 4 == 0)

# For Hypothesis to generate strings representing Q timestamps
q_timestamps = st.one_of(
    st.builds(
        lambda y, m, d, h, min, sec, ms: f'{y}.{m:02}.{d:02}D{h:02}:{min:02}:{sec:02}.{ms:03}',
        years, months, days, hours, minutes, seconds, milliseconds
    ),
    st.builds(
        lambda y, d, h, min, sec, ms: f'{y}.02.{d:02}D{h:02}:{min:02}:{sec:02}.{ms:03}',
        leap_years, february_days, hours, minutes, seconds, milliseconds
    )
)

@given(q_timestamps)
def test_timestamp_from_string(q_timestamp: str):
    assert TimeStamp.from_string(q_timestamp).datetime == datetime.strptime(q_timestamp, "%Y.%m.%dD%H:%M:%S.%f").replace(tzinfo=timezone.utc)

from hypothesis import given, strategies as st

@given(st.text(), st.text(min_size=1, max_size=1))
def test_eq_property(s: str, c: str):
    result = eq(s, c)
    assert len(result) == len(s)
    for i in range(len(s)):
        assert result[i] == int(s[i] == c)

def test_eq():
    assert eq("banana", "a") == [0, 1, 0, 1, 0, 1]
    assert eq("", "a") == []
    assert eq("aaaa", "a") == [1, 1, 1, 1]
    assert eq("bbbb", "a") == [0, 0, 0, 0]
