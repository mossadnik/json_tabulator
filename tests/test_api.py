"""Test documentation examples."""

from json_tabulator import query


def test_readme_example_query():
    data = {
        'id': 'doc-1',
        'table': [
            {'id': 1, 'name': 'row-1'},
            {'id': 2, 'name': 'row-2'}
        ]
    }

    my_query = query({
        'document_id': 'id',
        'row_id': 'table.*.id',
        'row_name': 'table.*.name'
    })

    rows = my_query.execute(data)

    expected = [
        {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
        {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
    ]

    assert list(rows) == expected


def test_query_array():
    data = [{'a': 1}]
    q = query({'x': '$.*.a'})
    actual = list(q.execute(data))
    assert actual == [{'x': 1}]
