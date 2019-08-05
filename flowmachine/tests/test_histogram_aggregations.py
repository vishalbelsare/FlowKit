# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flowmachine.core import make_spatial_unit
from flowmachine.features import (
    ModalLocation,
    daily_location,
    SubscriberHandsetCharacteristic,
)
import numpy as np

from flowmachine.features import Displacement, RadiusOfGyration, daily_location
from flowmachine.features.utilities.histogram_aggregations import HistogramAggregation
from flowmachine.features.subscriber.daily_location import locate_subscribers
from flowmachine.utils import list_of_dates


def test_create_histogram_using_integer_bins_value(get_dataframe):
    """
    Create histogram using one bins value.
    """
    RoG = RadiusOfGyration("2016-01-01", "2016-01-02")

    agg = HistogramAggregation(locations=RoG, bins=5)
    df = get_dataframe(agg)
    de = np.histogram(get_dataframe(RoG).value, bins=5)
    print("==================================")
    print(de)
    print("==================================")
    print(df.value.tolist())
    print("==================================")


def test_create_histogram_using_list_of_bins_values(get_dataframe):
    """
    Create histogram using list of bins values.
    """
    RoG = RadiusOfGyration("2016-01-01", "2016-01-02")

    agg = HistogramAggregation(locations=RoG, bins=[5, 10, 15, 20, 25, 30])
    df = get_dataframe(agg)
    de = np.histogram(get_dataframe(RoG).value, bins=[5, 10, 15, 20, 25, 30])
    print("==================================")
    print(de)
    print("==================================")
    print(df.value.tolist())
    print("==================================")


def test_create_histogram_using_bins_and_range_values(get_dataframe):
    """
    Create histogram using one bins and ranges value.
    """
    RoG = RadiusOfGyration("2016-01-01", "2016-01-02")

    agg = HistogramAggregation(locations=RoG, bins=5, ranges=(130.00, 230.00))
    df = get_dataframe(agg)
    de = np.histogram(get_dataframe(RoG).value, bins=5, range=(130.00, 230.00))
    print("==================================")
    print(de)
    print("==================================")
    print(df.value.tolist())
    print("==================================")
