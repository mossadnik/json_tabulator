from dataclasses import dataclass
import itertools as it


@dataclass(frozen=True)
class Star:
    pass


STAR = Star()


class Expression(tuple):
    def __repr__(self):
        return f'Expression({self.to_string()})'

    def to_string(self):
        def render_element(seg):
            if isinstance(seg, Star):
                return '*'
            elif isinstance(seg, str):
                return quote(seg)
            elif isinstance(seg, int):
                return str(seg)
            else:
                raise ValueError(f'Not a path segment: {seg}')

        return '.'.join(it.chain(['$'], map(render_element, self)))

    def __str__(self):
        return self.to_string()

    def _iter_generic(self):
        return (seg if isinstance(seg, str) else STAR for seg in self)

    def get_attribute(self):
        return Expression(self._iter_generic())

    def get_table(self):
        idx = -1
        for i, p in enumerate(self._iter_generic()):
            if not isinstance(p, str):
                idx = i
        return Expression(it.islice(self._iter_generic(), idx + 1))

    def is_valid(self):
        has_valid_elements = all(
            isinstance(value, str)
            or isinstance(value, int) and value >= 0
            or isinstance(value, Star)
            for value in self
        )
        return has_valid_elements and (self.is_generic() or self.is_concrete())

    def coincides_with(self, other):
        length = min(len(self), len(other))
        return self[:length] == other[:length]

    def get_row(self):
        idx = -1
        for i, seg in enumerate(self):
            if isinstance(seg, int):
                idx = i
            elif isinstance(seg, Star):
                raise ValueError(f'Cannot get row because path is not concrete: {self}.')
        return Expression(self[:idx + 1])

    def is_generic(self):
        return not any(isinstance(seg, int) for seg in self)

    def is_concrete(self):
        return not any(isinstance(seg, Star) for seg in self)

    def __add__(self, other):
        return Expression(super().__add__(other))


def expression(*args) -> Expression:
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        return Expression(args[0])
    return Expression(args)


def quote(s: str) -> str:
    require_quote = (
        s.isdigit()
        or s == '*'
        or '.' in s
    )
    if require_quote:
        return f'"{s}"'
    return s
