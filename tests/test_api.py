import pytest
from json_tabulator import tabulate, attribute
from json_tabulator.exceptions import ConversionFailed


class Test_tabulate_api:
    def test_names(self):
        query = tabulate({'a': '$.a', 'b': '$.*.b'})
        assert query.names == ['a', 'b']

    def test_fails_if_not_dict(self):
        with pytest.raises(TypeError):
            tabulate('$.*')  # type: ignore

    def test_accepts_dict_of_path_or_attribute(self):
        query = tabulate({'a': '$.a', 'b': attribute('$.b', converter=int)})
        a, b = query.attributes
        assert a.name == 'a'
        assert a.path == '$.a'
        assert a.converter is None
        assert b.name == 'b'
        assert b.path == '$.b'
        assert b.converter is int


class Test_Attribute:
    def test_path(self):
        query = tabulate({'a': '$.a[*].b'})
        a = query.attributes[0]
        assert a.path == '$.a[*].b'


class Test_converter:
    def test_applies_converter_to_value(self):
        query = tabulate({'a': attribute('$.a', converter=int)})
        data = {'a': '1'}
        actual = next(query.get_rows(data))
        assert actual['a'] == 1
        assert actual.errors == {}

    def test_passes_value_if_no_converter(self):
        query = tabulate({'a': attribute('$.a')})
        data = {'a': '1'}
        actual = next(query.get_rows(data))
        assert actual['a'] == '1'
        assert actual.errors == {}

    def test_does_not_apply_converter_if_no_value(self):
        """
        Check by applying int as a converter. int raises TypeError if applied to None.
        """
        query = tabulate({'a': attribute('$.a', converter=int)})
        data = {'a': None}
        actual = next(query.get_rows(data))
        assert actual['a'] is None
        assert actual.errors == {}

    def test_reports_ConversionFailed_if_converter_raises(self):
        query = tabulate({'a': attribute('$.a', converter=int)})
        data = {'a': 'abc'}
        actual = next(query.get_rows(data))
        assert actual['a'] is None
        err = actual.errors['a']
        assert isinstance(err, ConversionFailed)
        assert err.value == 'abc'
        assert isinstance(err.caused_by, ValueError)


class Test_default:
    @pytest.mark.parametrize('data', [{'a': None}, {}])
    def test_applies_default_value_if_no_value(self, data):
        query = tabulate({'a': attribute('$.a', default=1)})
        actual = next(query.get_rows(data))
        assert actual['a'] == 1

    def test_does_not_apply_default_if_value(self):
        query = tabulate({'a': attribute('$.a', default=1)})
        data = {'a': 0}
        actual = next(query.get_rows(data))
        assert actual['a'] == 0

    @pytest.mark.parametrize('data', [{'a': None}, {}])
    def test_applies_default_factory_if_no_value(self, data):
        query = tabulate({'a': attribute('$.a', default_factory=lambda: 1)})
        actual = next(query.get_rows(data))
        assert actual['a'] == 1

    def test_does_not_apply_default_factory_if_value(self):
        query = tabulate({'a': attribute('$.a', default_factory=lambda: 1)})
        data = {'a': 0}
        actual = next(query.get_rows(data))
        assert actual['a'] == 0

    def test_cannot_specify_default_and_default_factory(self):
        with pytest.raises(ValueError):
            attribute('$.a', default=1, default_factory=lambda: 1)
