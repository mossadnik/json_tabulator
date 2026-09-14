from dataclasses import dataclass
import itertools as it


@dataclass(frozen=True)
class Segment:
    pass


@dataclass(frozen=True)
class IndexStar(Segment):
    pass


@dataclass(frozen=True)
class KeyStar(Segment):
    pass


@dataclass(frozen=True)
class Index(Segment):
    def name(self):
        return 'index'


@dataclass(frozen=True)
class Path(Segment):
    def name(self):
        return 'path'


@dataclass(frozen=True)
class Inline(Segment):
    expression: 'Expression'

    def name(self):
        return 'inline'


INDEX_STAR = IndexStar()
KEY_STAR = KeyStar()
INDEX = Index()
PATH = Path()



def is_function(path: tuple):
    if not path:
        return False
    return isinstance(path[-1], (Index, Path, Inline))


class Expression(tuple):
    def to_string(self, absolute: bool=True) -> str:
        def render_element(seg):
            if seg is INDEX_STAR:
                return '[*]'
            elif seg is KEY_STAR:
                return '.*'
            elif isinstance(seg, (Path, Index)):
                return '.' + f'({seg.name()})'
            elif isinstance(seg, Inline):
                return '.' + f'({seg.name()} {seg.expression.to_string(absolute=False)})'
            elif isinstance(seg, str):
                return '.' + quote(seg, if_required=True)
            elif isinstance(seg, int):
                return f'[{seg}]'
            else:
                raise ValueError(f'Not a path segment: {seg}')

        elements = [map(render_element, self)]
        if absolute:
            elements = [['$']] + elements
        return ''.join(it.chain(*elements))

    def __str__(self) -> str:
        return self.to_string()

    def get_table(self) -> 'Expression':
        idx = -1
        for i, seg in enumerate(self):
            if seg in (INDEX_STAR, KEY_STAR):
                idx = i
        return Expression(self[:idx + 1])

    def coincides_with(self, other: 'Expression') -> bool:
        return all(a == b for a, b in zip(self, other))

    def is_concrete(self) -> bool:
        return not any(seg in (INDEX_STAR, KEY_STAR) for seg in self)

    def __add__(self, other: 'Expression') -> 'Expression':
        return Expression(super().__add__(other))


def expression(*args) -> Expression:
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        return Expression(args[0])
    return Expression(args)


def quote(s: str, if_required: bool = True) -> str:
    if not s:
        return s
    require_quote = (
        not if_required
        or s[0].isdigit()
        or any(c in s for c in '$*.[]()"\'')
    )
    if require_quote:
        return '"{}"'.format(s.replace('"', '\\"'))
    return s
