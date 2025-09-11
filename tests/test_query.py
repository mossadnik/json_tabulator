import pytest
from typing import Generator
from json_tabulator import tabulate


def test_raises_for_invalid_queries():
    """
    A query is invalid if it requests attributes from tables whose
    Expressions do not all coincide.
    """
    with pytest.raises(ValueError):
        tabulate({
            'a_b': '$.a[*].b',
            'x_y': '$.x[*].y',
        })


def test_returns_row_generator_for_valid_queries():
    query = tabulate({
        'a_b': '$.a[*].b',
        'x_y': '$.x.y',
    })
    data = {
        'a': [{'b': 'a_b_0'}, {'b': 'a_b_1'}],
        'x': {'y': 'x_y'}
    }
    actual = query.get_rows(data)
    assert isinstance(actual, Generator)
    rows = list(actual)
    assert rows == [
        {'a_b': 'a_b_0', 'x_y': 'x_y'},
        {'a_b': 'a_b_1', 'x_y': 'x_y'}
    ]


def test_optionally_omits_missing_attributes():
    query = tabulate(
        {'a': 'a', 'b': 'b'},
        omit_missing_attributes=True
    )
    data = {'b': 'b'}
    actual = list(query.get_rows(data))
    assert actual == [{'b': 'b'}]


def test_optionally_missing_attributes_are_set_to_None():
    query = tabulate(
        {'a': 'a', 'b': 'b'},
        omit_missing_attributes=False
    )
    data = {'b': 'b'}
    rows = list(query.get_rows(data))
    assert rows == [{'a': None, 'b': 'b'}]


def test_INDEX_with_array():
    query = tabulate({'key': 'a[*].(index)'})
    data = {'a': [0, 1, 2]}
    rows = list(query.get_rows(data))
    assert rows == [{'key': 0}, {'key': 1}, {'key': 2}]


def test_PATH_with_array():
    query = tabulate({'path': 'a[*].(path)'})
    data = {'a': [0, 1, 2]}
    rows = list(query.get_rows(data))
    assert rows == [{'path': '$.a[0]'}, {'path': '$.a[1]'}, {'path': '$.a[2]'}]


def test_fixed_array_index():
    query = tabulate({'x': '$[1].a'})
    data = [{'a': 0}, {'a': 1}]
    rows = list(query.get_rows(data))
    assert rows == [{'x': 1}]


def test_STAR_with_dict():
    query = tabulate({'x': '*.a'})
    data = {'a': {'a': 1}, 'b': {'a': 2}}
    rows = list(query.get_rows(data))
    assert rows == [{'x': 1}, {'x': 2}]


def test_INDEX_with_dict():
    query = tabulate({'x': '$.*.(index)'})
    data = {'a': {'a': 1}, 'b': {'a': 2}}
    rows = list(query.get_rows(data))
    assert rows == [{'x': 'a'}, {'x': 'b'}]


def test_query_array():
    data = [{'a': 1}]
    q = tabulate({'x': '$[*].a'})
    actual = list(q.get_rows(data))
    assert actual == [{'x': 1}]
