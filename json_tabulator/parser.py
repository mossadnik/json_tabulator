
from .expression import Expression, Key, Index, Star

from parsy import string, regex, eof, alt, ParseError


dot = string('.')
star = string('*').result(Star())
root = string('$')
forbidden = ''.join(['"', "'", '.', '$', '*'])
end_of_segment = eof | dot


def make_quoted_key(q: str):
    return string(q) >> regex(f'({2 * q}|[^{q}])+') << string(q)

key = regex(f'[^{forbidden}]+').map(Key)
quoted_key = (make_quoted_key('"') | make_quoted_key("'")).map(Key)
number = regex(r'\d+').map(lambda x: Index(int(x)))

def segment_with_ending(ending):
  return alt(*[p << ending for p in [number, quoted_key, key, star]])


expression = alt(
    root.optional() >> eof.result([]),
    (root + dot).optional() >> (segment_with_ending(dot).many() + segment_with_ending(eof).map(lambda s: [s])),
)

class InvalidExpression(ValueError):
    pass


def parse_expression(string: str) -> Expression:
    try:
        return Expression(expression.parse(string))
    except ParseError:
        raise InvalidExpression(string)
