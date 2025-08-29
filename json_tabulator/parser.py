from enum import Enum
import itertools as it

from .expression import Expression, Key, Star


class State(Enum):
    start_segment = 0
    within_segment = 1
    end_segment = 2
    double_quotes = 3
    single_quotes = 4
    start_expression = 5


class InvalidExpression(ValueError):
    pass


def error(s, i):
    raise InvalidExpression(f'Parsing expression {s}, failed at position {i}')


def parse_expression(s: str) -> Expression:
    return Expression(_parse(s))


def _parse_segment(s, start, stop):
    if start is None:
        return None
    text = s[start:stop]
    if text == '*':
        return Star()
    else:
        return Key(text)


def _parse(s: str):
    state = State.start_expression
    i_token = 0
    for i, c in enumerate(it.chain(s, [None])):
        if state == State.start_expression and c in ('$', None):
            if c == '$' and i == 0:
                state = State.end_segment
                i_token = None
        elif state in (State.start_segment, State.start_expression):
            if c in ['"', "'"]:
                state = State.double_quotes if c == '"' else State.single_quotes
                i_token = i + 1
            elif c in ['.', None]:
                error(s, i)
            else:
                state = State.within_segment
                i_token = i
        elif state == State.within_segment:
            if c in ['.', None]:
                segment = _parse_segment(s, i_token, i)
                if segment:
                    yield segment
                state = State.start_segment
                i_token = i + 1
            else:
                pass
        elif state == State.end_segment:
            if c in ['.', None]:
                segment = _parse_segment(s, i_token, i)
                if segment:
                    yield segment
                state = State.start_segment
                i_token = i + 1
            else:
                error(s, i)
        elif state in [State.double_quotes, State.single_quotes]:
            quote = {State.double_quotes: '"', State.single_quotes: "'"}[state]
            if c == quote:
                yield Key(s[i_token:i])
                i_token = None
                state = State.end_segment
