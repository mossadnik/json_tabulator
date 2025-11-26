# json_tabulator

A simple query language for extracting tables from JSON-like objects.

Working with tabular data is much easier than working with nested documents. json_tabulator helps to extract tables from JSON-like objects in a simple, declarative manner. All further processing is left to the many powerful tools that exist for working with tables, such as Spark or Pandas.


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
    'row_id': 'table[*].id',
    'row_name': 'table[*].name'
})

rows = query.get_rows(data)
```

This returns an iterator of rows, where each row is of type `Row`, which is a subclass of `dict`. A row maps attribute names to values. In addition, extraction errors are reported in the attribute `Row.errors`.

```python
>>> list(rows)
[
    {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
    {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
]
```

### Path Syntax

The syntax for path expressions is very similar to a subset of JSON Path. A path consists of an optional root element `'$'` followed by a path that specifies what is to be extracted. The child operator `.` and subscripts `[1], ['a'], [*]` can be used for arrays or dicts.

#### Dict key

Can be any string. Key values can be quoted with single or double quotes. Within quoted strings, the quote character must be doubled to escape it. For example, `"say \"hello\""` is interpreted as `say "hello"`.

Keys _must_ be quoted if
* they contain any of the characters `* $ . ' " [] ()`, or if
* they start with a digit
* they are used in a subscript, e.g. `$["child"]` is valid, but `$[child]` is not.

#### Subscripts

Subscripts are entered as `[]`. Allowed subscript values are

* Non-negative numbers representing array indices, e.g. `$[123]`
* Quoted dict keys, e.g. `$['a']`
* Wildcards, e.g. `$[*]`

Subscripts can be entered with or without a period, e.g. `$[*]` and `$.[*]` are both valid.

#### Wildcard `*`

An asterisk `*` is interpreted as a wildcard. Iterates over dict values or array items. Note that wildcards _must_ be entered explicitly, there is no implicit iteration over arrays. A wildcard for dict keys can be entered like `.*` or `[*]`. For arrays only `[*]` is allowed. This is the same behavior as for JSON Path.

#### Functions

Functions are enclosed in parentheses. All available functions can only appear at the end of a path, separated by a `.`. Example: `$.*.(path)`.

##### Structural Queries

There are two functions that query document structure:

* `(index)` returns the index that corresponds to the preceding wildcard
* `(path)` returns the full path up to the preceding wildcard

They _must_ be placed directly after a wildcard and must be at the end of the path. For example `*.(index)` is valid, but `a.(index)` and `*.(index).b` are not.

The output of `(path)` is unique for all rows extracted from the document.

##### Inline Arrays

The function `(inline <relative-path>)` allows to return multiple values in a single row as an inline array. The argument `<relative-path>` follows the same rules as other paths with the exception that the initial `$` is forbidden.

For example, the query `$.a[*].(inline b[*].c)` finds all elements that match the path `$.a[*].b[*].c` but aggregates them into lists, one per each match of `$.a[*]`.

### Data Extraction

#### Query Semantics

Values for all attributes in a query are combined into individual rows. Attributes from different parts of the document are combined by "joining" on the lowest common ancestor.

For this reason, all wildcards for all attributes must lie on a common path. Violating this condition would lead to implicit cross joins and the associated data blow-up.

For example, the paths `$.a[*]` and `$.b[*]` cannot be combined because the wildcards are not on the same path. On the other hand, `$.a` and `$.b[*].c` can be combined.

Queries are analysed and compiled independently of the data to be queried.

If you think you need to get a combination of attributes that is not allowed, think again. If you still think so just run multiple queries and do the join afterwards.

#### Returned values

By default, all extracted values are returned as-is with no further conversion. Returned values are not limited to atomic types, dicts and lists are also allowed.

All rows contain all keys in the order that is specified in the query, regardless of whether the attribute is missing.

In the query it is possible to specify processing of returned values by using the function `json_tabulator.attribute` instead of passing a path. You can configure a `converter` function and `default` value or `default_factory`. Converters are only run on values that are not missing, otherwise the default is applied. For example,

```python
from json_tabulator import tabulate, attribute

query = tabulate({
    'x': attribute('$[*].a', converter=lambda x: str(x), default='nothing')
})

data = [
    {'a': 1},
    {'a': None},
    {}
]
[row['x'] for row in query.get_rows(data)]

# output
['1', 'nothing', 'nothing']
```


### Error Reporting

The returned rows are of type `Row` which is a subclass of dict. It has an additional attribute `Row.errors` that is a dict mapping attributes to errors. There are two possible errors:

1. If the path to an attribute does not exist, the error is `AttributeNotFound`.
2. If a converter raises an exception the error is `ConversionFailed` with details about the source value and exception that caused the conversion to fail.

Example:

```python
from json_tabulator import tabulate, attribute
from json_tabulator.exceptions import AttributeNotFound, ConversionFailed

query = tabulate({
    'a': '$.a',
    'b': attribute('$.b', converter=int)
})
data = {'b': 'not a number'}

row = next(query.get_rows(data))

assert isinstance(row.errors['a'], AttributeNotFound)
assert isinstance(row.errors['b'], ConversionFailed)

assert row.errors['b'].value == 'not a number'
assert isinstance(row.errors['b'].caused_by, ValueError)
```

## Related Projects

- [jsontable](https://pypi.org/project/jsontable/) has the same purpose but is not maintained.
- [jsonpath-ng](https://github.com/bridgecrewio/jsonpath-ng) and other jsonpath implementation are much more flexible but more cumbersome to extract nested tables.
