import pytest
from json_tabulator.expression import INDEX_STAR, KEY_STAR, INDEX, PATH, Inline, expression
from json_tabulator.parser import parse_expression, InvalidExpression


@pytest.mark.parametrize('s, expected', [
    ['a', ('a',)],
    ['a.b', ('a', 'b')],
    ['a.*', ('a', KEY_STAR)],
    ['a[*]', ('a', INDEX_STAR)],
    ['a.[*]', ('a', INDEX_STAR)],
    ['*', (KEY_STAR,)],
    ['"\\"a\\""', ('"a"',)],
    ["'\\'a\\''", ("'a'",)],
    ['a[1][2]', ('a', 1, 2)],
    ['a.[1].[2]', ('a', 1, 2)],
    ['"123"', ('123',)],
    ['"123"', ('123',)],
    ['*.b', (KEY_STAR, 'b')],
    # functions
    ['*.(index)', (KEY_STAR, INDEX)],
    ['*.(path)', (KEY_STAR, PATH)],
    ['a.(inline [*].b)', ('a', Inline(expression(INDEX_STAR, 'b')))]
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
    'a["123"]',  # don't allow dict keys in square brackets
    "a['123']",
])
def test_rejects(s):
    with pytest.raises(InvalidExpression):
        parse_expression(s)
