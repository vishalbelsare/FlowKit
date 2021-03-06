# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marshmallow import fields, post_load
from marshmallow.validate import OneOf
from marshmallow_oneofschema import OneOfSchema

from flowmachine.features.location.redacted_spatial_aggregate import (
    RedactedSpatialAggregate,
)
from flowmachine.features.location.spatial_aggregate import SpatialAggregate
from .base_exposed_query import BaseExposedQuery
from .base_schema import BaseSchema
from .daily_location import DailyLocationSchema
from .modal_location import ModalLocationSchema

__all__ = [
    "SpatialAggregateSchema",
    "SpatialAggregateExposed",
    "InputToSpatialAggregate",
]


class InputToSpatialAggregate(OneOfSchema):
    type_field = "query_kind"
    type_schemas = {
        "daily_location": DailyLocationSchema,
        "modal_location": ModalLocationSchema,
    }


class SpatialAggregateExposed(BaseExposedQuery):
    def __init__(self, *, locations):
        # Note: all input parameters need to be defined as attributes on `self`
        # so that marshmallow can serialise the object correctly.
        self.locations = locations

    @property
    def _flowmachine_query_obj(self):
        """
        Return the underlying flowmachine object.

        Returns
        -------
        Query
        """
        locations = self.locations._flowmachine_query_obj
        return RedactedSpatialAggregate(
            spatial_aggregate=SpatialAggregate(locations=locations)
        )


class SpatialAggregateSchema(BaseSchema):
    # query_kind parameter is required here for claims validation
    query_kind = fields.String(validate=OneOf(["spatial_aggregate"]))
    locations = fields.Nested(InputToSpatialAggregate, required=True)

    __model__ = SpatialAggregateExposed
