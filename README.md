# Dynamic Distributed Merging
[![Tests](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/test.yml)
[![Linting](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/lint.yml)
[![Coverage Status](https://coveralls.io/repos/github/TheWozard/dynamic-distributed-merging/badge.svg?branch=master)](https://coveralls.io/github/TheWozard/dynamic-distributed-merging?branch=master)

A POC concept for an algorithm for merging distributed json documents with dynamic sub object priority.

## Problem
A set of json documents need to be deeply merged together. Documents contain potentially overlapping objects,lists,and fields. Documents may have different merge orders per element in the document. There may only be a section of the data the final merge is interested in or there may be sections of the final data that are meant to be hidden or controlled.

## Idea
Use of a "context" to specify how different sections of the data behave and are to be treated.
This context specifies a scope and attributes that govern that scope.

| Attribute | Type | Default | Description |
| :- | :- | :- | :- |
| Priority | `int` | `0` | The merge order priority for this element and all sub elements. Highest value gets merged on top. Negative numbers allowed.
| Order | `int` | `0` | Intended to break Priority ties, as such each order should be unique and potentially derived at runtime. Lowest value wins. This represents the original order the documents were submitted to be merged, so that in the event of a tie the original order would be upheld despite documents being in a potentially unknown order during traversal.
| Terminal | `bool` | `false` | When evaluating the merge of an object or array resolution starts from the top down. Any document can chose to terminate this progress early. Any nodes resolved will remain but no later documents will be processed for any missing nodes. Does not effect the resolution of individual values, in that case use 'Allow None' with a higher priority
| Allow None | `bool` | `false` | When a resolved value is found, should we consider None to be a valid one. Behaves slightly differently between values and arrays/objects. In the case of values a value that is None will be skipped over for consideration in the merge unless it has a context of True for Allow None. In the case of arrays/objects when a node is resolved, if the resolving value is None it will by default be discarded, unless the array/object has an Allow None of True.
| Allow Empty | `bool` | `false` | Does not affect value resolution. Decides if when an array/list is resolved if an empty array/list should be returned or by default a None is returned in its place

The core concept is expandable with new features in the case of more control being needed

> It was previously considered the inclusion of a "method" attribute that controlled the behavior of Terminal, Allow None, and Allow Empty. This was discarded as an implementation detail of the parser and not the core algorithm

### Providing the Context
There isn't a requirement on how the context be provided, only that it be traversable alongside the document. For the sake of visualization what follows are some examples of providing the context in the same document to be extracted before traversal.

#### Embedded
```JSON
{
    "$priority": 2,
    "data": "...",
    "object": {
        "$terminal": true,
        "data": "...",
    }
}
```
#### Metadata-Path
```JSON
{
    "$merge": [
        {
            "scope": "$.object",
            "priority": 1,
        }
    ],
    "data": "...",
    "object": {
        "data": "...",
    }
}
```
#### Independent Document
```JSON
{
    "$meta-merge-doc": "https://document.host/merge/schemaV1",
    "data": "...",
    "object": {
        "data": "...",
    }
}
```

## Pros
- The originator gains control over the merge order of their document
- Declarative approach makes simpler to understand data lineage of the final document
- Allows dynamic fallback of data if documents are unable to be sourced
- Build in migration support between sources through having new source with a higher priority. Data will automatically fall back to old source as the new one builds out its features.

## Cons
- Merging of lists has multiple issues
    - Merging objects in lists requires an id be established
    - De-duplication
    - Ordering
- Provides no central authority and relies on all sources cooperating

## Advanced Techniques/Features

### Control Document
With the inclusion of a single highest priority document with a root `terminal=true` you can extract a subset of the data without processing the merge for the entire object

```JSON
[{
    "$terminal": true,
    "data": null,
},
{
    "data": "Success",
    "extra": "Failure"
}]
```
would result in
```JSON
{
    "data": "Success",
}
```
as only the first document gets traversed.

### Data Suppression
Through a combination usage of `terminal=true` and `allow_none=true` a higher tier document with no data and only a context can take control of specific nodes and values during resolution and prevent them from being resolved

> TODO: Example of this