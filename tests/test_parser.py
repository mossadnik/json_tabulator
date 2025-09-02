import pytest
from json_tabulator.expression import Key, Star, Index
from json_tabulator.parser import parse_expression, InvalidExpression


@pytest.mark.parametrize('s, expected', [
    ['', ()],
    ['a', (Key('a'),)],
    ['a.b', (Key('a'), Key('b'))],
    ['a.*', (Key('a'), Star())],
    ['*', (Star(),)],
    ['123abc', (Key('123abc'),)],
    ['123', (Index(123),)],
    ['"123"', (Key('123'),)],
    ['"123"', (Key('123'),)],
])
def test_accepts(s, expected):
    """
    - Paths may contain array wildcards or string keys.
    - A root prefix '$' is optional
    """
    assert parse_expression(s) == expected
    prefixed = '$.' + s if s else '$' + s
    assert parse_expression(prefixed) == expected


@pytest.mark.parametrize('s', [
    'a..b',
    'a.',
    '.',
    '$.',
    '*abc',
    'a"bc',
    "a'bc",
])
def test_rejects(s):
    with pytest.raises(InvalidExpression):
        parse_expression(s)
