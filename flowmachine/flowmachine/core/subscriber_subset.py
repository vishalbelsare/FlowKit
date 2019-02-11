# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from abc import abstractmethod
from .query import Query


class SubscriberSubsetBase(Query):
    """
    Base class for the different types of subscriber subsets.
    """

    @property
    @abstractmethod
    def is_proper_subset(self):
        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not implement 'is_proper_subset'"
        )

    @abstractmethod
    def apply_subset(self, sql):
        raise NotImplementedError(
            f"Class {self.__class__.__name__} does not implement 'apply_subset'"
        )

    def _get_query_attrs_for_dependency_graph(self, analyse=False):
        attrs = {}
        attrs["name"] = self.__class__.__name__
        attrs["stored"] = "N/A"
        attrs["cost"] = "N/A"
        attrs["runtime"] = "N/A"
        return attrs


class AllSubscribers(SubscriberSubsetBase):

    is_proper_subset = False

    def _make_query(self):
        return "<AllSubscribers>"

    def apply_subset(self, sql):
        return sql


class SubsetFromFlowmachineQuery(SubscriberSubsetBase):

    is_proper_subset = True

    def __init__(self, query):
        self.ORIG_SUBSET_TODO_REMOVE_THIS = query

    def _make_query(self):
        return "<SubsetFromFlowmachineQuery>"

    def apply_subset(self, sql):
        raise NotImplementedError()


class ExplicitSubset(SubscriberSubsetBase):

    is_proper_subset = True

    def __init__(self, subset):
        self.ORIG_SUBSET_TODO_REMOVE_THIS = subset

    def _make_query(self):
        return "<ExplicitSubset>"

    def apply_subset(self, sql):
        raise NotImplementedError()


class OtherSubset(SubscriberSubsetBase):

    is_proper_subset = True

    def __init__(self, subset):
        self.ORIG_SUBSET_TODO_REMOVE_THIS = subset

    def get_query(self):
        return self.ORIG_SUBSET_TODO_REMOVE_THIS.get_query()

    def _make_query(self):
        return "<OtherSubset>"

    def apply_subset(self, sql):
        raise NotImplementedError()


def make_subscriber_subset(subset):
    if isinstance(subset, SubscriberSubsetBase):
        return subset
    elif subset == "all" or subset is None:
        return AllSubscribers()
    elif isinstance(subset, (list, tuple)):
        return ExplicitSubset(subset)
    elif isinstance(subset, Query):
        return SubsetFromFlowmachineQuery(subset)
    # else:
    #     return OtherSubset(subset)
    else:
        raise ValueError(f"Invalid subscriber subset: {subset!r}")
