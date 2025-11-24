import pytest
from typing import Generator
from json_tabulator import tabulate, Row
from json_tabulator.exceptions import IncompatiblePaths, AttributeNotFound


def test_raises_for_invalid_queries():
    """
    A query is invalid if it requests attributes from tables whose
    Expressions do not all coincide.
    """
    with pytest.raises(IncompatiblePaths):
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
    assert all(isinstance(row, Row) for row in rows)
    assert rows == [
        {'a_b': 'a_b_0', 'x_y': 'x_y'},
        {'a_b': 'a_b_1', 'x_y': 'x_y'}
    ]


class Test_reports_AttributeNotFound:
    def test_errors_simple(self):
        query = tabulate({'a': '$[*].a'})
        data = [{'a': 1}, {}]
        rows = list(query.get_rows(data))
        assert rows[0].errors == {}
        actual = rows[1].errors
        assert isinstance(actual, dict)
        assert set(actual.keys()) == {'a'}
        assert isinstance(actual['a'], AttributeNotFound)

    def test_errors_nested(self):
        """Check that errors are passed on when nesting."""
        query = tabulate({'x': '$[*].a[*].x', 'y': '$[*].y'})
        data = [{'a': [{'x': 1}, {'x': 2}]}]
        rows = list(query.get_rows(data))
        assert len(rows) == 2
        for row in rows:
            assert set(row.errors.keys()) == {'y'}
            assert isinstance(row.errors['y'], AttributeNotFound)

    def test_inline(self):
        query = tabulate({'a': '$.(inline a[*])'})
        data = {}
        rows = list(query.get_rows(data))
        assert len(rows) == 1
        row = rows[0]
        assert set(row.keys()) == {'a'}
        assert row['a'] is None
        assert set(row.errors.keys()) == {'a'}
        assert isinstance(row.errors['a'], AttributeNotFound)


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


@pytest.mark.parametrize('path, expected', [
    ('$[1]', [{'x': None}]),
    ('$[1][*]', [])
])
def test_INDEX_out_of_range(path, expected):
    """Fixed array indices behave like dict keys."""
    data = [[1]]
    q = tabulate({'x': path})
    actual = list(q.get_rows(data))
    assert actual == expected


def test_inline():
    data = {'a': [{'b': 1}, {'b': 2}]}
    q = tabulate({'x': '$.a.(inline [*].b)'})
    actual = list(q.get_rows(data))
    expected = [{'x': [1, 2]}]
    assert actual == expected
