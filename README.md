# Dynamic Distributed Merging
[![Tests](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/test.yml)
[![Linting](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/TheWozard/dynamic-distributed-merging/actions/workflows/lint.yml)

A POC concept for a protocol for merging distributed json documents with dynamic sub object priority.

## Problem
A set of json documents need to be deeply merged together. Documents contain potentially overlapping objects,lists,and fields. Documents may have different merge orders per element in the document.

## Idea
Use of imbedded fields to specify *Priority* and *Join* method

A context is provided alongside the document that specifies the scopes for 2 attributes

| Attribute | Type | Default | Description |
| :- | :- | :- | :- |
| Priority | Int | 0 | The merge order priority for this element and all sub elements. Highest value gets merged on top. Negative numbers allowed.
| Method | String/Enum | "outer" | The method to be used to merge documents with all documents below it. This is resolved from lowest `Priority` to highest with the higher document determining the `Method`

### Providing the Context
The context can be provided in a couple forms

#### Embedded
```JSON
{
    "$priority": 2,
    "$method": "outer",
    "data": "...",
    "object": {
        "$priority": -1,
        "$method": "outer",
        "data": "...",
    }
}
```
#### Metadata-Path
```JSON
{
    "$meta-merge": [
        {
            "scope": "$.object",
            "priority": 1,
            "method": "outer"
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
- Declarative approach makes simpler to review
- Allows dynamic fallback of data is documents are unable to be sourced
- Makes moving ownership of document elements between sources easier as the new host can claim Priority while the data is removed from the old source.

## Cons
- Merging or lists has multiple issues
    - Merging objects in lists requires an id be established
    - De-duplication
    - Ordering
- Provides no central authority and relies on all sources cooperating
    - Could be solved by setting max priorities per source.