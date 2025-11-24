import typing as tp


class InvalidExpression(ValueError):
    pass


class IncompatiblePaths(ValueError):
    pass


class AttributeNotFound(ValueError):
    pass


class ConversionFailed(ValueError):
    def __init__(self, msg: str, value: tp.Any, caused_by: tp.Optional[Exception] = None):
        super().__init__(msg)
        self.value = value
        self.caused_by = caused_by
