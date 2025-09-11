import pytest
from json_tabulator.expression import expression, STAR, INDEX, PATH


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
    [('a', STAR, 'b'), ('a', STAR)],
    [('a', 'b'), ()],
    [('a', STAR, INDEX), ('a', STAR)],
    [('a', 1), ()],
])
def test_get_table(path: tuple, expected: tuple):
    """
    - get_table returns the path up to the last STAR element.
    - This path corresponds to a sub-table in the JSON document.
    """
    path, expected = expression(path), expression(expected)
    actual = path.get_table()
    assert actual == expected



@pytest.mark.parametrize('obj', [STAR])
def test_Segments_are_hashable(obj):
    hash(obj)  # does not raise


@pytest.mark.parametrize('path, expected', [
    [(), '$'],
    [('a', STAR), '$.a[*]'],
    ['*', '$."*"'],
    [('a', '*'), '$.a."*"'],
    ['123', '$."123"'],
    ['.', '$."."'],
    ['a.b.c', '$."a.b.c"'],
    [1, '$[1]'],
    [(STAR, INDEX), '$[*].(index)'],
    [(STAR, PATH), '$[*].(path)']
])
def test_expression_path_string(path, expected):
    actual = expression(path).to_string()
    assert actual == expected
