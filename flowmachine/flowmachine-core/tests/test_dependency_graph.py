# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for flowmachine_core dependency graph functions
"""
import pytest
import re
import textwrap
import IPython
from io import StringIO

from flowmachine_core.utility_queries.custom_query import CustomQuery
from query_bases.dummy_query import DummyQuery
from flowmachine_core.core.subscriber_subsetter import make_subscriber_subsetter
from flowmachine_core.utility_queries.event_table_subset import EventTableSubset

from flowmachine_core.core.dependency_graph import (
    print_dependency_tree,
    calculate_dependency_graph,
    unstored_dependencies_graph,
    plot_dependency_graph,
    store_queries_in_order,
)


def test_print_dependency_tree(deeply_nested_test_query):
    """
    Test that the expected dependency tree is printed for a nested query.
    """

    expected_output = textwrap.dedent(
        """\
        <Query of type: Nested, query_id: 'xxxxx'>
          - <Query of type: Nested, query_id: 'xxxxx'>
             - <Query of type: CustomQuery, query_id: 'xxxxx'>
        """
    )

    s = StringIO()
    print_dependency_tree(deeply_nested_test_query, stream=s)
    output = s.getvalue()
    output_with_query_ids_replaced = re.sub(r"\b[0-9a-f]+\b", "xxxxx", output)

    assert expected_output == output_with_query_ids_replaced


def test_calculate_dependency_graph(deeply_nested_test_query, test_query):
    """
    Test that calculate_dependency_graph() runs and the returned graph has some correct entries.
    """
    G = calculate_dependency_graph(deeply_nested_test_query, analyse=True)

    assert f"x{test_query.query_id}" in G.nodes()
    assert (
        G.nodes[f"x{test_query.query_id}"]["query_object"].query_id
        == test_query.query_id
    )


def test_unstored_dependencies_graph():
    """
    Test that unstored_dependencies_graph returns the correct graph in an example case.
    """
    # Create dummy queries with dependency structure
    #
    #           5:unstored
    #            /       \
    #       3:stored    4:unstored
    #      /       \     /
    # 1:unstored   2:unstored
    #
    # Note: we add a string parameter to each query so that they have different query IDs
    dummy1 = DummyQuery(dummy_param=["dummy1"])
    dummy2 = DummyQuery(dummy_param=["dummy2"])
    dummy3 = DummyQuery(dummy_param=["dummy3", dummy1, dummy2])
    dummy4 = DummyQuery(dummy_param=["dummy4", dummy2])
    dummy5 = DummyQuery(dummy_param=["dummy5", dummy3, dummy4])
    dummy3.store()

    expected_query_nodes = [dummy2, dummy4]
    graph = unstored_dependencies_graph(dummy5)
    assert not any(dict(graph.nodes(data="stored")).values())
    assert len(graph) == len(expected_query_nodes)
    for query in expected_query_nodes:
        assert f"x{query.query_id}" in graph.nodes()
        assert (
            graph.nodes[f"x{query.query_id}"]["query_object"].query_id == query.query_id
        )


def test_unstored_dependencies_graph_for_stored_query():
    """
    Test that the unstored dependencies graph for a stored query is empty.
    """
    dummy1 = DummyQuery(dummy_param=["dummy1"])
    dummy2 = DummyQuery(dummy_param=["dummy2"])
    dummy3 = DummyQuery(dummy_param=["dummy3", dummy1, dummy2])
    dummy3.store()

    graph = unstored_dependencies_graph(dummy3)
    assert len(graph) == 0


def test_plot_dependency_graph(nested_test_query):
    """
    Test that plot_dependency_graph() runs and returns the expected IPython.display objects.
    """
    output_svg = plot_dependency_graph(nested_test_query, format="svg")
    output_png = plot_dependency_graph(
        nested_test_query, format="png", width=600, height=200
    )

    assert isinstance(output_svg, IPython.display.SVG)
    assert isinstance(output_png, IPython.display.Image)
    assert output_png.width == 600
    assert output_png.height == 200

    with pytest.raises(ValueError, match="Unsupported output format: 'foobar'"):
        plot_dependency_graph(nested_test_query, format="foobar")


def test_store_queries_in_order():
    """
    Test that store_queries_in_order() stores each query's dependencies before storing that query itself.
    """

    class QueryWithStoreAssertions(DummyQuery):
        def store(self):
            for query in self.dependencies:
                assert query.is_stored
            super().store()

    dummy1 = QueryWithStoreAssertions(dummy_param=["dummy1"])
    dummy2 = QueryWithStoreAssertions(dummy_param=["dummy2"])
    dummy3 = QueryWithStoreAssertions(dummy_param=["dummy3", dummy1, dummy2])
    dummy4 = QueryWithStoreAssertions(dummy_param=["dummy4", dummy2])
    dummy5 = QueryWithStoreAssertions(dummy_param=["dummy5", dummy3, dummy4])
    graph = calculate_dependency_graph(dummy5)
    store_queries_in_order(graph)