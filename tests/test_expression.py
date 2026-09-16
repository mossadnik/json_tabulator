import pytest
from json_tabulator.expression import expression, INDEX_STAR, KEY_STAR, INDEX, PATH, Inline


@pytest.mark.parametrize('expr,expected', [
    [('a', 'b'), False],
    [('a', INDEX_STAR, 'b'), True],
    [('a', KEY_STAR, 'b'), True],
    [('a', 0, 'b'), False],
    [('a', 0, 'b', INDEX_STAR), True],
    [('a', 0, 'b', KEY_STAR), True],
])
def test_has_wildcards(expr: tuple, expected: bool):
    """
    - A path is concrete if it does not contain the wildcard STAR.
    """
    expr = expression(expr)
    assert expr.has_wildcards() == expected


@pytest.mark.parametrize('this, other, expected', [
    [('a', 'b'), ('a', 'b'), True],
    [('a',), ('a', 'b'), True],
    [('a', 'b'), ('a', ('c')), False],
    [('a', INDEX_STAR, 'b'), ('a', INDEX_STAR), True],
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
    [('a', INDEX_STAR, 'b'), ('a', INDEX_STAR)],
    [('a', 'b'), ()],
    [('a', INDEX_STAR, INDEX), ('a', INDEX_STAR)],
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



@pytest.mark.parametrize('obj', [INDEX_STAR])
def test_Segments_are_hashable(obj):
    hash(obj)  # does not raise


@pytest.mark.parametrize('path, expected', [
    [(), '$'],
    [('a', INDEX_STAR), '$.a[*]'],
    [('a', KEY_STAR), '$.a.*'],
    ['*', '$."*"'],
    [('a', '*'), '$.a."*"'],
    ['123', '$."123"'],
    ['.', '$."."'],
    ['a.b.c', '$."a.b.c"'],
    [1, '$[1]'],
    [(INDEX_STAR, INDEX), '$[*].(index)'],
    [(INDEX_STAR, PATH), '$[*].(path)'],
    [('a', Inline(expression(INDEX_STAR, 'b'))), '$.a.(inline [*].b)'],
])
def test_expression_path_string(path, expected):
    actual = expression(path).to_string()
    assert actual == expected


def test_expression_path_to_string_raises():
    with pytest.raises(ValueError):
        expression(1.0).to_string()


@pytest.mark.parametrize('expr, expected', [
    [('a', 1, 'b'), ('a', INDEX_STAR, 'b')],
    [('a', 'b'), ('a', 'b')],
    [(1, KEY_STAR), (INDEX_STAR, KEY_STAR)]
])
def test_get_selector(expr, expected):
    actual = expression(expr).get_selector()
    expected = expression(expected)
    assert actual == expected
