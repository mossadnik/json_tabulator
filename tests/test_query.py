import pytest
from typing import Generator
from json_tabulator.query import QueryPlan
from json_tabulator.expression import Expression, Star, Key


def test_raises_for_invalid_queries():
    """
    A query is invalid if it requests attributes from tables whose
    Expressions do not all coincide.
    """
    query = {
        'a_b': Expression((Key('a'), Star(), Key('b'))),
        'x_y': Expression((Key('x'), Star(), Key('y')))
    }
    with pytest.raises(ValueError):
        QueryPlan.from_dict(query)


def test_returns_row_generator_for_valid_queries():
    query = {
        'a_b': Expression((Key('a'), Star(), Key('b'))),
        'x_y': Expression((Key('x'), Key('y')))
    }
    data = {
        'a': [{'b': 'a_b_0'}, {'b': 'a_b_1'}],
        'x': {'y': 'x_y'}
    }
    actual = QueryPlan.from_dict(query).execute(data, omit_missing_attributes=False)
    assert isinstance(actual, Generator)
    rows = list(actual)
    assert rows == [
        {'a_b': 'a_b_0', 'x_y': 'x_y'},
        {'a_b': 'a_b_1', 'x_y': 'x_y'}
    ]


def test_optionally_omits_missing_attributes():
    query = {'a': Expression((Key('a'),)), 'b': Expression((Key('b'),))}
    data = {'b': 'b'}
    rows = list(QueryPlan.from_dict(query).execute(data, omit_missing_attributes=True))
    assert rows == [{'b': 'b'}]


def test_optionally_missing_attributes_are_set_to_None():
    query = {'a': Expression((Key('a'),)), 'b': Expression((Key('b'),))}
    data = {'b': 'b'}
    rows = list(QueryPlan.from_dict(query).execute(data, omit_missing_attributes=False))
    assert rows == [{'a': None, 'b': 'b'}]
