# json_tabulator

A simple query language for extracting tables from JSON-like objects.

Working with tabular data is much easier than working with nested documents. json-tables helps to extract tables from JSON-like objects in a simple, declarative manner. All further processing is left to the many powerful tools that exist for working with tables, such as Spark or Pandas.


## Installation

Install from pypi:

```shell
pip install json_tabulator
```

## Quickstart

The `json_tabulator` module provides tools to extract a JSON document into a set of related tables. Let's start with a simple document

```python
data = {
    'id': 'doc-1',
    'table': [
        {'id': 1, 'name': 'row-1'},
        {'id': 2, 'name': 'row-2'}
    ]
}
```

The document consists of a document-level value `id` as well as a nested sub-table `table`. We want to extract it into a single table, with the global value folded into the table.

To do this, we write a query that defines the conversion into a table like this:

```python
from json_tabulator import tabulate

query = tabulate({
    'document_id': 'id',
    'row_id': 'table.*.id',
    'row_name': 'table.*.name'
})

rows = query.get_rows(data)
```

This returns an iterator of rows, where each row is a dict `{<column_name>: <value>}`:

```python
>>> list(rows)
[
    {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
    {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
]
```

## Related Projects

- [jsontable](https://pypi.org/project/jsontable/) has the same purpose but is not maintained.
- [jsonpath-ng](https://github.com/bridgecrewio/jsonpath-ng) and other jsonpath implementation are much more flexible but more cumbersome to extract nested tables.
