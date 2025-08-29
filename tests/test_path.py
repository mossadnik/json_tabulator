import pytest
from json_tabulator.expression import Expression, Star, Key, Index


@pytest.mark.parametrize('path,expected', [
    [(Key('a'), Index(0), Key('b')), True],
    [(Key('a'), Star(), Key('b')), True],
    [(Index(1), Key('a')), True],
    [(Key('a'), Index(-1)), False],
    [(Index(1), Index(2)), True],
    [(Star(), Star()), True],
    [(Index(2), Star()), False],
])
def test_is_valid(path: tuple, expected: bool):
    """
    - A valid path may contain keys, non-negative array indices or the wildcard '*'.
    - A valid path must not use both array indices and the wildcard.
    """
    path = Expression(path)
    assert path.is_valid() == expected


@pytest.mark.parametrize('path,expected', [
    [(Key('a'), Key('b')), True],
    [(Key('a'), Star(), Key('b')), True],
    [(Key('a'), Index(0), Key('b')), False],
    [(Key('a'), Index(0), Key('b'), Star()), False]
])
def test_is_generic(path: tuple, expected: bool):
    """
    - A path is generic if it does not contain array indices.
    """
    path = Expression(path)
    assert path.is_generic() == expected


@pytest.mark.parametrize('path,expected', [
    [(Key('a'), Key('b')), True],
    [(Key('a'), Star(), Key('b')), False],
    [(Key('a'), Index(0), Key('b')), True],
    [(Key('a'), Index(0), Key('b'), Star()), False]
])
def test_is_concrete(path: tuple, expected: bool):
    """
    - A path is concrete if it does not contain the wildcard Star().
    """
    path = Expression(path)
    assert path.is_concrete() == expected


@pytest.mark.parametrize('this, other, expected', [
    [(Key('a'), Key('b')), (Key('a'), Key('b')), True],
    [(Key('a'),), (Key('a'), Key('b')), True],
    [(Key('a'), Key('b')), (Key('a'), Key('c')), False],
    [(Key('a'), Star(), Key('b')), (Key('a'), Star()), True],
    [(Key('a'), Index(0), Key('b')), (Key('a'), Index(0)), True],
    [(Key('a'), Index(0), Key('b')), (Key('a'), Index(1)), False]
])
def test_coincides_with(this: tuple, other: tuple, expected: bool):
    """
    - Two paths coincide if one is a prefix of the other.
    - Coincidence is symmetric
    """
    this, other = Expression(this), Expression(other)
    assert this.coincides_with(other) == expected
    assert other.coincides_with(this) == expected


@pytest.mark.parametrize('path, expected', [
    [(Key('a'), Index(0), Key('b')), (Key('a'), Star(), Key('b'))],
    [(Key('a'), Star(), Key('b')), (Key('a'), Star(), Key('b'))],
    [(Key('a'), Key('b')), (Key('a'), Key('b'))]
])
def test_get_attribute(path: tuple, expected: tuple):
    """
    - get_attribute replaces all array indices with Star(), returning a generic path
    - This path can be used to select the path as an attribute in a table
    """
    path, expected = Expression(path), Expression(expected)
    actual = path.get_attribute()
    assert actual == expected
    assert actual.is_generic()


@pytest.mark.parametrize('path, expected', [
    [(Key('a'), Index(0), Key('b')), (Key('a'), Star())],
    [(Key('a'), Star(), Key('b')), (Key('a'), Star())],
    [(Key('a'), Key('b')), ()]
])
def test_get_table(path: tuple, expected: tuple):
    """
    - get_table returns the generic path up to the last Star() element.
    - This path corresponds to a sub-table in the JSON document.
    """
    path, expected = Expression(path), Expression(expected)
    actual = path.get_table()
    assert actual == expected
    assert actual.is_generic()


@pytest.mark.parametrize('path, expected', [
    [(Key('a'), Index(0), Key('b')), (Key('a'), Index(0))],
    [(Key('a'), Index(0), Key('b'), Index(1), Key('c')), (Key('a'), Index(0), Key('b'), Index(1))],
    [(Key('a'), Key('b')), ()],
])
def test_get_row(path: tuple, expected: tuple):
    """
    - get_row returns the concrete path up the last array index.
    - This path is a unique row identifier across all extracted tables from a JSON document.
    """
    path, expected = Expression(path), Expression(expected)
    actual = path.get_row()
    assert actual == expected
    assert actual.is_concrete()


def test_get_row_raises_if_path_not_concrete():
    """Rows can only be computed from concrete paths."""
    path = Expression((Key('a'), Star()))
    with pytest.raises(ValueError):
        path.get_row()


@pytest.mark.parametrize('obj', [Key('a'), Index(1), Star])
def test_Segments_are_hashable(obj):
    hash(obj)  # does not raise
