import json

from hashlib import md5
from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf, Length
from marshmallow_oneofschema import OneOfSchema

from flowmachine.core.dummy_query import DummyQuery


#
# Flowmachine query schemas
#


class DummyQuerySchema(Schema):
    """
    Dummy query useful for testing.
    """

    dummy_param = fields.String(required=True)

    @post_load
    def make_query_object(self, params):
        return DummyQueryExposed(**params)


class DailyLocationSchema(Schema):
    date = fields.Date(required=True)
    method = fields.String(required=True, validate=OneOf(["last", "most-common"]))
    aggregation_unit = fields.String(
        required=True, validate=OneOf(["admin0", "admin1", "admin2", "admin3"])
    )
    subscriber_subset = fields.String(
        required=False, allow_none=True, validate=OneOf([None])
    )

    @post_load
    def make_query_object(self, params):
        return DailyLocationExposed(**params)


class InputToModalLocationSchema(OneOfSchema):
    type_field = "query_kind"
    type_schemas = {"daily_location": DailyLocationSchema}

    def get_obj_type(self, obj):
        if isinstance(obj, DailyLocationExposed):
            return "daily_location"
        else:
            raise Exception("Unknown object type: {obj.__class__.__name__}")


class ModalLocationSchema(Schema):
    locations = fields.Nested(
        InputToModalLocationSchema, many=True, validate=Length(min=1)
    )
    aggregation_unit = fields.String(
        validate=OneOf(["admin0", "admin1", "admin2", "admin3"])
    )
    subscriber_subset = fields.String(allow_none=True, validate=OneOf([None]))

    @post_load
    def make_query_object(self, data):
        return ModalLocationExposed(**data)


class FlowmachineQuerySchema(OneOfSchema):
    type_field = "query_kind"
    type_schemas = {
        "daily_location": DailyLocationSchema,
        "modal_location": ModalLocationSchema,
        "dummy_query": DummyQuerySchema,
    }

    def get_obj_type(self, obj):
        if isinstance(obj, DailyLocationExposed):
            return "daily_location"
        elif isinstance(obj, ModalLocationExposed):
            return "modal_location"
        else:
            raise Exception("Unknown object type: {obj.__class__.__name__}")


#
# Flowmachine query objects
#


class BaseExposedQuery:
    """
    Base class for exposed flowmachine queries.

    Note: these classes are not meant to be instantiated directly!
    Instead, they are instantiated automatically through the query
    schema classes above.
    """

    @property
    def __schema__(self):
        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not have the __schema__ property set."
        )

    @property
    def query_id(self):
        return md5(json.dumps(self.query_params, sort_keys=True).encode()).hexdigest()

    @property
    def query_params(self):
        """
        Return the parameters from which the query is constructed. Note that this
        includes the parameters of any subqueries of which it is composed.

        Returns
        -------
        dict
            JSON representation of the query parameters, including those of subqueries.
        """
        marshmallow_schema = self.__schema__()
        return marshmallow_schema.dump(self)


class DummyQueryExposed(BaseExposedQuery):

    __schema__ = DummyQuerySchema

    def __init__(self, dummy_param):
        self.dummy_param = dummy_param

    @property
    def _flowmachine_query_obj(self):
        return DummyQuery(dummy_param=self.dummy_param)


class DailyLocationExposed(BaseExposedQuery):

    __schema__ = DailyLocationSchema

    def __init__(self, date, *, method, aggregation_unit, subscriber_subset=None):
        self.date = date
        self.method = method
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset


class ModalLocationExposed(BaseExposedQuery):

    __schema__ = ModalLocationSchema

    def __init__(self, locations, *, aggregation_unit, subscriber_subset=None):
        self.locations = locations
        self.aggregation_unit = aggregation_unit
        self.subscriber_subset = subscriber_subset
