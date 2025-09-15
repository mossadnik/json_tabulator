import itertools as it
import enum


class Segment(enum.Enum):
    star = enum.auto()
    index = enum.auto()
    path = enum.auto()


STAR = Segment.star
INDEX = Segment.index
PATH = Segment.path


def is_function(path: tuple):
    if len(path) != 1:
        return False
    return path[0] in (INDEX, PATH)


class Expression(tuple):

    def to_string(self):
        def render_element(seg):
            if seg is STAR:
                return '[*]'
            elif seg in (PATH, INDEX):
                return '.' + f'({seg.name})'
            elif isinstance(seg, str):
                return '.' + quote(seg, if_required=True)
            elif isinstance(seg, int):
                return f'[{seg}]'
            else:
                raise ValueError(f'Not a path segment: {seg}')

        return ''.join(it.chain(['$'], map(render_element, self)))

    def __str__(self):
        return self.to_string()

    def get_table(self):
        idx = -1
        for i, seg in enumerate(self):
            if seg is STAR:
                idx = i
        return Expression(self[:idx + 1])

    def coincides_with(self, other):
        return all(a == b for a, b in zip(self, other))

    def is_concrete(self):
        return not any(seg is STAR for seg in self)

    def __add__(self, other):
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
