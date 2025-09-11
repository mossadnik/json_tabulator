"""Test documentation examples."""

from json_tabulator import tabulate


def test_readme_example_query():
    data = {
        'id': 'doc-1',
        'table': [
            {'id': 1, 'name': 'row-1'},
            {'id': 2, 'name': 'row-2'}
        ]
    }

    query = tabulate({
        'document_id': 'id',
        'row_id': 'table[*].id',
        'row_name': 'table[*].name'
    })

    rows = query.get_rows(data)

    expected = [
        {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
        {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
    ]

    assert list(rows) == expected
