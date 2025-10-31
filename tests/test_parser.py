import pytest
from json_tabulator.expression import STAR, INDEX, PATH, Inline, expression
from json_tabulator.parser import parse_expression, InvalidExpression


@pytest.mark.parametrize('s, expected', [
    ['a', ('a',)],
    ['a.b', ('a', 'b')],
    ['a.*', ('a', STAR)],
    ['a[*]', ('a', STAR)],
    ['a.[*]', ('a', STAR)],
    ['*', (STAR,)],
    ['"\\"a\\""', ('"a"',)],
    ["'\\'a\\''", ("'a'",)],
    ['a["123"]', ('a', '123')],
    ["a['123']", ('a', '123')],
    ['a[1]["cd"]', ('a', 1, 'cd')],
    ['a.[1].["cd"]', ('a', 1, 'cd')],
    ['"123"', ('123',)],
    ['"123"', ('123',)],
    ['*.b', (STAR, 'b')],
    # functions
    ['*.(index)', (STAR, INDEX)],
    ['*.(path)', (STAR, PATH)],
    ['a.(inline [*].b)', ('a', Inline(expression(STAR, 'b')))]
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
    '',
    '*abc',
    'a"bc',
    "a'bc",
    '(notafunction)',
    '(index)',
    '(path)',
    '*.(index).a',  # function followed by other segment
    '*.(path).a',
    '123abc',  # unquoted key starting with number
    '123',
    'a.(inline $[*])',  # absolute path in inline
])
def test_rejects(s):
    with pytest.raises(InvalidExpression):
        parse_expression(s)
