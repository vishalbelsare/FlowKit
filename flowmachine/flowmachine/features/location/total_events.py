# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# -*- coding: utf-8 -*-

from typing import List, Union

"""
Calculates the number of events at a location
during a specified time period.



"""
from ...core import location_joined_query, make_spatial_unit
from ..utilities import EventsTablesUnion

from ...core import Query
from ...core.mixins import GeoDataMixin


class TotalLocationEvents(GeoDataMixin, Query):
    """
    Calculates the total number of events on an hourly basis
    per location (such as a tower or admin region),
    and per interaction type.

    Parameters
    ----------
    start : str
        ISO format date string to at which to start the analysis
    stop : str
        As above for the end of the analysis
    table : str, default 'all'
        Specifies a table of cdr data on which to base the analysis. Table must
        exist in events schema. If 'all' then we use all tables specified in
        flowmachine.yml.
    spatial_unit : flowmachine.core.spatial_unit.*SpatialUnit, default cell
        Spatial unit to which subscriber locations will be mapped. See the
        docstring of make_spatial_unit for more information.
    interval : ['hour', 'day', 'min']
        Records activity on an hourly, daily, or by minute level.
    direction : str, default 'both'
        Look only at incoming or outgoing events. Can be either
        'out', 'in' or 'both'.
    """

    allowed_intervals = {"day", "hour", "min"}

    def __init__(
        self,
        start: str,
        stop: str,
        *,
        table: Union[None, List[str]] = None,
        spatial_unit=make_spatial_unit("cell"),
        interval: str = "hour",
        direction: str = "both",
        hours="all",
        subscriber_subset=None,
        subscriber_identifier="msisdn",
    ):
        self.start = start
        self.stop = stop
        self.table = table
        self.spatial_unit = spatial_unit
        self.interval = interval
        self.direction = direction

        if self.interval not in self.allowed_intervals:
            raise ValueError(
                "'Interval must be one of: {} got: {}".format(
                    self.allowed_intervals, self.interval
                )
            )

        self.time_cols = ["(datetime::date)::text AS date"]
        if self.interval == "hour" or self.interval == "min":
            self.time_cols.append("extract(hour FROM datetime) AS hour")
        if self.interval == "min":
            self.time_cols.append("extract(minute FROM datetime) AS min")

        events_tables_union_cols = ["location_id", "datetime"]
        # if we need to filter on outgoing/incoming calls, we will also fetch this
        # column. Don't fetch it if it is not needed for both efficiency and the
        # possibility that we might want to do pass another data type which does not
        # have this information.
        if self.direction != "both":
            events_tables_union_cols += ["outgoing"]
        if self.direction not in ["in", "out", "both"]:
            raise ValueError("Unrecognised direction: {}".format(self.direction))

        self.unioned = location_joined_query(
            EventsTablesUnion(
                self.start,
                self.stop,
                tables=self.table,
                columns=events_tables_union_cols,
                hours=hours,
                subscriber_subset=subscriber_subset,
                subscriber_identifier=subscriber_identifier,
            ),
            spatial_unit=self.spatial_unit,
            time_col="datetime",
        )
        super().__init__()

    @property
    def column_names(self) -> List[str]:
        return (
            self.spatial_unit.location_id_columns
            + [x.split(" AS ")[1] for x in self.time_cols]
            + ["total"]
        )

    def _make_query(self):
        # Set a filter clause based on the direction of the event
        if self.direction == "both":
            filter_clause = ""
        elif self.direction == "in":
            filter_clause = "WHERE NOT outgoing"
        elif self.direction == "out":
            filter_clause = "WHERE outgoing"
        else:
            raise ValueError("Unrecognised direction: {}".format(self.direction))

        # list of columns that we want to group by, these are all the time
        # columns, plus the location columns
        groups = [
            x.split(" AS ")[0] for x in self.time_cols
        ] + self.spatial_unit.location_id_columns

        # We now need to group this table by the relevant columns in order to
        # get a count per region
        sql = f"""
            SELECT
                {', '.join(self.spatial_unit.location_id_columns)},
                {', '.join(self.time_cols)},
                count(*) AS total
            FROM
                ({self.unioned.get_query()}) unioned
            {filter_clause}
            GROUP BY
                {', '.join(groups)}
        """

        return sql
