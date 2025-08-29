import pytest
from json_tables.expression import Key, Star
from json_tables.parser import parse_expression, InvalidExpression


@pytest.mark.parametrize('s, expected', [
    ['', ()],
    ['a', (Key('a'),)],
    ['a.b', (Key('a'), Key('b'))],
    ['a.*', (Key('a'), Star())],
    ['*', (Star(),)],
])
def test_accepts(s, expected):
    """
    - Paths may contain array wildcards, array indices, or strings different from array markers. TODO
    """
    assert parse_expression(s) == expected


@pytest.mark.parametrize('s', [
    'a..b',
    'a.',
    '.',
])
def test_rejects(s):
    with pytest.raises(InvalidExpression):
        parse_expression(s)
