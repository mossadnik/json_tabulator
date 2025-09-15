import pytest
from json_tabulator import tabulate


class Test_Tabulator:
    def test_names(self):
        query = tabulate({'a': '$.a', 'b': '$.*.b'})
        assert query.names == ['a', 'b']

    def test_fails_if_not_dict(self):
        with pytest.raises(ValueError):
            tabulate('$.*')


class Test_Attribute:
    def test_path(self):
        query = tabulate({'a': '$.a[*].b'})
        a = query.attributes[0]
        assert a.path == '$.a[*].b'
