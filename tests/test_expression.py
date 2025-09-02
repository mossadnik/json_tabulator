import pytest
from json_tabulator.expression import expression, STAR


@pytest.mark.parametrize('path,expected', [
    [('a', 0, 'b'), True],
    [('a', STAR, 'b'), True],
    [(1, 'a'), True],
    [('a', -1), False],
    [(1, 2), True],
    [(STAR, STAR), True],
    [(2, STAR), False],
])
def test_is_valid(path: tuple, expected: bool):
    """
    - A valid path may contain keys, non-negative array indices or the wildcard '*'.
    - A valid path must not use both array indices and the wildcard.
    """
    path = expression(path)
    assert path.is_valid() == expected


@pytest.mark.parametrize('path,expected', [
    [('a', 'b'), True],
    [('a', STAR, 'b'), True],
    [('a', 0, 'b'), False],
    [('a', 0, 'b', STAR), False]
])
def test_is_generic(path: tuple, expected: bool):
    """
    - A path is generic if it does not contain array indices.
    """
    path = expression(path)
    assert path.is_generic() == expected


@pytest.mark.parametrize('path,expected', [
    [('a', 'b'), True],
    [('a', STAR, 'b'), False],
    [('a', 0, 'b'), True],
    [('a', 0, 'b', STAR), False]
])
def test_is_concrete(path: tuple, expected: bool):
    """
    - A path is concrete if it does not contain the wildcard STAR.
    """
    path = expression(path)
    assert path.is_concrete() == expected


@pytest.mark.parametrize('this, other, expected', [
    [('a', 'b'), ('a', 'b'), True],
    [('a',), ('a', 'b'), True],
    [('a', 'b'), ('a', ('c')), False],
    [('a', STAR, 'b'), ('a', STAR), True],
    [('a', 0, 'b'), ('a', 0), True],
    [('a', 0, 'b'), ('a', 1), False]
])
def test_coincides_with(this: tuple, other: tuple, expected: bool):
    """
    - Two paths coincide if one is a prefix of the other.
    - Coincidence is symmetric
    """
    this, other = expression(this), expression(other)
    assert this.coincides_with(other) == expected
    assert other.coincides_with(this) == expected


@pytest.mark.parametrize('path, expected', [
    [('a', 0, 'b'), ('a', STAR, 'b')],
    [('a', STAR, 'b'), ('a', STAR, 'b')],
    [('a', 'b'), ('a', 'b')]
])
def test_get_attribute(path: tuple, expected: tuple):
    """
    - get_attribute replaces all array indices with STAR, returning a generic path
    - This path can be used to select the path as an attribute in a table
    """
    path, expected = expression(path), expression(expected)
    actual = path.get_attribute()
    assert actual == expected
    assert actual.is_generic()


@pytest.mark.parametrize('path, expected', [
    [('a', 0, 'b'), ('a', STAR)],
    [('a', STAR, 'b'), ('a', STAR)],
    [('a', 'b'), ()]
])
def test_get_table(path: tuple, expected: tuple):
    """
    - get_table returns the generic path up to the last STAR element.
    - This path corresponds to a sub-table in the JSON document.
    """
    path, expected = expression(path), expression(expected)
    actual = path.get_table()
    assert actual == expected
    assert actual.is_generic()


@pytest.mark.parametrize('path, expected', [
    [('a', 0, 'b'), ('a', 0)],
    [('a', 0, 'b', 1, ('c')), ('a', 0, 'b', 1)],
    [('a', 'b'), ()],
])
def test_get_row(path: tuple, expected: tuple):
    """
    - get_row returns the concrete path up the last array index.
    - This path is a unique row identifier across all extracted tables from a JSON document.
    """
    path, expected = expression(path), expression(expected)
    actual = path.get_row()
    assert actual == expected
    assert actual.is_concrete()


def test_get_row_raises_if_path_not_concrete():
    """Rows can only be computed from concrete paths."""
    path = expression('a', STAR)
    with pytest.raises(ValueError):
        path.get_row()


@pytest.mark.parametrize('obj', [STAR])
def test_Segments_are_hashable(obj):
    hash(obj)  # does not raise


@pytest.mark.parametrize('path, expected', [
    [(), '$'],
    [('a', STAR), '$.a.*'],
    ['*', '$."*"'],
    [('a', '*'), '$.a."*"'],
    ['123', '$."123"'],
    ['.', '$."."'],
    ['a.b.c', '$."a.b.c"'],
    [1, '$.1'],
])
def test_expression_path_string(path, expected):
    actual = expression(path).to_string()
    assert actual == expected
