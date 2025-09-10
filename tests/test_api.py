from json_tabulator import tabulate


class Test_Tabulator:
    def test_names(self):
        query = tabulate({'a': '$.a', 'b': '$.*.b'})
        assert query.names == ['a', 'b']
