from typing import Any
from dataclasses import dataclass
from collections import defaultdict

from .expression import Expression, STAR


def nested_get(data, keys) -> tuple[Any, bool]:
    res = data
    for k in keys:
        if not isinstance(res, dict) or k not in res:
            return None, False
        res = res[k]
    return res, True


@dataclass
class QueryPlan:
    path: Expression
    extracts: dict[Expression, dict[str, tuple]]

    @classmethod
    def from_dict(cls, query: dict[str, Expression]) -> 'QueryPlan':
        steps = defaultdict(dict)
        query_path = Expression()
        for name, expr in query.items():
            table = expr.get_table()

            if not table.coincides_with(query_path):
                raise ValueError(f'Illegal query: Paths {table} and {query_path} are not compatible.')

            query_path = max(query_path, table, key=len)
            steps[table][name] = tuple(seg for seg in expr[len(table):])

        return cls(path=query_path, extracts=steps)

    def execute(self, data, omit_missing_attributes: bool):
        def _recurse(data, head, tail, path, extract):
            if head in self.extracts:
                update = (
                    (name, *nested_get(data, keys))
                    for name, keys in self.extracts[head].items()
                )
                extract = {
                    **extract,
                    **{
                        name: value
                        for name, value, success in update
                        if success or not omit_missing_attributes
                    }
                }
            if tail:
                current, tail = tail[0], tail[1:]
                head = head + (current,)
                if current is STAR and isinstance(data, list):
                    for idx, item in enumerate(data):
                        yield from _recurse(item, head, tail, path + (idx,), extract)
                elif isinstance(data, dict):
                    yield from _recurse(data.get(current), head, tail, path + (current,), extract)
            else:
                yield extract

        yield from _recurse(data, Expression(), self.path, (), {})
