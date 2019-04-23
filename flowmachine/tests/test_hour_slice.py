# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from operator import ge as greater_or_equal, lt as less_than

from flowmachine.core.sqlalchemy_table_definitions import EventsCallsTable
from flowmachine.core.sqlalchemy_utils import get_string_representation
from flowmachine.core.hour_slice import HourOfDay, HourInterval, HourSlice


def test_filter_by_hour_of_day():
    hd = HourOfDay(hour_str="09:00")
    expr = hd.filter_timestamp_column(
        EventsCallsTable.datetime, cmp_op=greater_or_equal
    )
    expected = "to_char(events.calls.datetime, 'HH24:MI') >= '09:00'"
    assert expected == get_string_representation(expr)

    hd = HourOfDay(hour_str="12:40")
    expr = hd.filter_timestamp_column(EventsCallsTable.datetime, cmp_op=less_than)
    expected = "to_char(events.calls.datetime, 'HH24:MI') < '12:40'"
    assert expected == get_string_representation(expr)

    hd = HourOfDay(hour_str=None)
    expr = hd.filter_timestamp_column(EventsCallsTable.datetime, cmp_op=less_than)
    expected = "true"
    assert expected == get_string_representation(expr)


def test_invalid_input_format():
    with pytest.raises(
        ValueError, match="Input argument must be a string the format 'HH:MM'."
    ):
        HourOfDay(hour_str=99999)
    with pytest.raises(ValueError, match="Hour string must have the format 'HH:MM'"):
        HourOfDay(hour_str="999:999")
    with pytest.raises(ValueError, match="Invalid hour value"):
        HourOfDay(hour_str="99:99")
    with pytest.raises(ValueError, match="Invalid minutes value"):
        HourOfDay(hour_str="14:99")


def test_compare_hour_of_day():
    hd1 = HourOfDay(hour_str="11:50")
    hd2 = HourOfDay(hour_str="13:20")
    hd3 = HourOfDay(hour_str=None)

    assert hd1 == hd1 == "11:50"
    assert hd2 == hd2 == "13:20"
    assert hd3 == hd3 == None
    assert hd1 != hd2
    assert hd1 != hd3

    with pytest.raises(
        TypeError, match="HourOfDay cannot be compared to object of type <class 'int'>"
    ):
        hd1 == 42


def test_daily_hour_slice():
    hs = HourInterval(start_hour="00:00", stop_hour="06:30", freq="day")
    assert hs.start_hour == "00:00"
    assert hs.stop_hour == "06:30"
    assert hs.period.freq == "day"

    expr = hs.filter_timestamp_column(EventsCallsTable.datetime)
    expected = "to_char(events.calls.datetime, 'HH24:MI') >= '00:00' AND to_char(events.calls.datetime, 'HH24:MI') < '06:30'"
    assert expected == get_string_representation(expr)


def test_daily_hour_slice_without_start_hour():
    hs = HourInterval(start_hour=None, stop_hour="17:50", freq="day")
    assert hs.start_hour == None
    assert hs.stop_hour == "17:50"
    assert hs.period.freq == "day"

    expr = hs.filter_timestamp_column(EventsCallsTable.datetime)
    expected = "to_char(events.calls.datetime, 'HH24:MI') < '17:50'"
    assert expected == get_string_representation(expr)


def test_daily_hour_slice_without_stop_hour():
    hs = HourInterval(start_hour="07:20", stop_hour=None, freq="day")
    assert hs.start_hour == "07:20"
    assert hs.stop_hour == None
    assert hs.period.freq == "day"

    expr = hs.filter_timestamp_column(EventsCallsTable.datetime)
    expected = "to_char(events.calls.datetime, 'HH24:MI') >= '07:20'"
    assert expected == get_string_representation(expr)


def test_weekly_hour_slice():
    hs = HourInterval(
        start_hour="04:00", stop_hour="07:45", freq="week", weekday="tuesday"
    )
    assert hs.start_hour == "04:00"
    assert hs.stop_hour == "07:45"
    assert hs.period.freq == "week"
    assert hs.period.weekday == "Tuesday"

    ts_col = EventsCallsTable.datetime
    expr = hs.filter_timestamp_column(ts_col)
    expected = (
        "to_char(events.calls.datetime, 'HH24:MI') >= '04:00' AND "
        "to_char(events.calls.datetime, 'HH24:MI') < '07:45' AND "
        "EXTRACT(dow FROM events.calls.datetime) = 2"
    )
    assert expected == get_string_representation(expr)


def test_weekly_hour_slice_without_start_value():
    hs = HourInterval(
        start_hour=None, stop_hour="16:38", freq="week", weekday="Wednesday"
    )
    assert hs.start_hour == None
    assert hs.stop_hour == "16:38"
    assert hs.period.freq == "week"
    assert hs.period.weekday == "Wednesday"

    ts_col = EventsCallsTable.datetime
    expr = hs.filter_timestamp_column(ts_col)
    expected = (
        "to_char(events.calls.datetime, 'HH24:MI') < '16:38' AND "
        "EXTRACT(dow FROM events.calls.datetime) = 3"
    )
    assert expected == get_string_representation(expr)


def test_weekly_hour_slice_without_stop_value():
    hs = HourInterval(
        start_hour="10:00", stop_hour=None, freq="week", weekday="Saturday"
    )
    assert hs.start_hour == "10:00"
    assert hs.stop_hour == None
    assert hs.period.freq == "week"
    assert hs.period.weekday == "Saturday"

    ts_col = EventsCallsTable.datetime
    expr = hs.filter_timestamp_column(ts_col)
    expected = (
        "to_char(events.calls.datetime, 'HH24:MI') >= '10:00' AND "
        "EXTRACT(dow FROM events.calls.datetime) = 6"
    )
    assert expected == get_string_representation(expr)


def test_invalid_arguments():
    with pytest.raises(
        ValueError, match="Argument `freq` must be one of: 'day', 'week'."
    ):
        HourInterval(start_hour="00:00", stop_hour="08:00", freq="foobar")

    with pytest.raises(
        ValueError, match="If freq='week' then the `weekday` argument must be provided."
    ):
        HourInterval(start_hour="00:00", stop_hour="08:00", freq="week", weekday=None)

    with pytest.raises(ValueError, match="Invalid value for `weekday`."):
        HourInterval(
            start_hour="00:00", stop_hour="08:00", freq="week", weekday="foobar"
        )

    with pytest.raises(
        ValueError,
        match="If freq='day' then the `weekday` argument must not be provided.",
    ):
        HourInterval(
            start_hour="00:00", stop_hour="08:00", freq="day", weekday="Monday"
        )


def test_multiple_our_slices():
    hs1 = HourInterval(start_hour="08:00", stop_hour="16:30", freq="day")
    hs2 = HourInterval(
        start_hour="10:00", stop_hour="18:45", freq="week", weekday="Thursday"
    )
    mhs = HourSlice(hour_intervals=[hs1, hs2])

    ts_col = EventsCallsTable.datetime
    expr = mhs.get_subsetting_condition(ts_col)
    expected = (
        "to_char(events.calls.datetime, 'HH24:MI') >= '08:00' AND "
        "to_char(events.calls.datetime, 'HH24:MI') < '16:30' OR "
        "to_char(events.calls.datetime, 'HH24:MI') >= '10:00' AND "
        "to_char(events.calls.datetime, 'HH24:MI') < '18:45' AND "
        "EXTRACT(dow FROM events.calls.datetime) = 4"
    )
    assert expected == get_string_representation(expr)
