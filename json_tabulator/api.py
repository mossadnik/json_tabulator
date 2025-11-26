from dataclasses import dataclass, replace
import typing as tp
from .expression import Expression
from .query import QueryPlan, Row
from .parser import parse_expression
from .exceptions import ConversionFailed


@dataclass
class Attribute:
    expression: Expression
    name: tp.Optional[tp.Hashable] = None
    converter: tp.Optional[tp.Callable[[tp.Any], tp.Any]] = None
    default: tp.Optional[tp.Any] = None
    default_factory: tp.Optional[tp.Callable[[], tp.Any]] = None

    @property
    def path(self):
        """Return query path expression."""
        return self.expression.to_string()


def attribute(
        path: str,
        converter: tp.Optional[tp.Callable[[tp.Any], tp.Any]] = None,
        default: tp.Optional[tp.Any] = None,
        default_factory: tp.Optional[tp.Callable[[], tp.Any]] = None
):
    if default is not None and default_factory is not None:
        raise ValueError('Cannot specify both default and default_value.')
    return Attribute(
        expression=parse_expression(path),
        converter=converter,
        default=default,
        default_factory=default_factory
    )


@dataclass
class Tabulator:
    """JSON tabulator query.

    Attributes:
        attributes: Output attributes.
    """
    attributes: list[Attribute]
    _plan: QueryPlan

    @property
    def names(self) -> list[tp.Hashable]:
        """Returns the names of all attributes."""
        return [a.name for a in self.attributes]

    def get_rows(self, data: tp.Any) -> tp.Generator[Row, None, None]:
        """Run query against Python object.

        Yields:
            dict[str, typ.Any]: Row generator.
        """

        return (
            _apply_converters(row, self.attributes)
            for row in self._plan.execute(data)
        )


def _apply_converters(row: Row, attributes: list[Attribute]) -> Row:
    errors = row.errors

    def apply_converter(attr, value):
        if value is None:
            if attr.default_factory is not None:
                return attr.default_factory()
            else:
                return attr.default
        elif attr.converter is None:
            return value
        else:
            try:
                return attr.converter(value)
            except Exception as e:
                errors[attr.name] = ConversionFailed(
                    f'Conversion failed with unhandled exception {type(e)}',
                    value=value,
                    caused_by=e
                )

    data = {a.name: apply_converter(a, row[a.name]) for a in attributes}
    return Row(data=data, errors=errors)


def tabulate(
        attributes: dict[str, tp.Union[str, Attribute]],
) -> Tabulator:
    """Create a new query.

    Args:
        attributes: A dict mapping attribute names to path expressions.
        omit_missing_attributes: Controls output for attributes that are not found.
            If False (default), attributes are set to `None`.
            If True, the keys are omitted on row level.

    Returns:
        A `Tabulator` object that represents the query. The query can be run against data
        by calling `Tabulator.get_rows(data)`.

    Raises:
        InvalidExpression: If path expression contains invalid syntax.
        IncompatiblePaths: If requested paths are not compatible due to requesting
            data that requires an implicit cross join.
    """
    def handle_attribute(name: tp.Hashable, attr: tp.Union[str, Attribute]) -> Attribute:
        if isinstance(attr, str):
            return Attribute(expression=parse_expression(attr), name=name)
        elif isinstance(attr, Attribute):
            return replace(attr, name=name)
        else:
            raise TypeError(f'Expected str or Attribute, got {type(attr)}')

    if isinstance(attributes, dict):
        parsed_attributes = [
            handle_attribute(name, attr)
            for name, attr in attributes.items()
        ]
    else:
        raise TypeError(f'Query not understood: {attributes}')
    plan = QueryPlan.from_dict({a.name: a.expression for a in parsed_attributes})
    return Tabulator(parsed_attributes, plan)
