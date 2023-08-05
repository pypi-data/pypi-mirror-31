# Boolean Search for Python Containers

Library to make simple boolean queries for python string containers (e.g. sets or lists).
E.g. query built from expression 'Alice & Bob & ~John' can be applied to any container to check if it contains strings 'Alice' and 'Bob' and not contains 'John'.

Base example:

```python
#!/usr/bin/env python

from termsquery import TermsQuery

query = TermsQuery('Alice & (Bob | "Unknown user")')

container1 = {'Alice', 'Unknown user'}
container2 = {'Bob'}

assert True == query(container1)
assert False == query(container2)
```

Library can be used to tag collection of documents: create query for each tag
and apply that query for document words.

Simple tagging example:

```python
#!/usr/bin/env python

from termsquery import TermsQuery

tags = {
    'A-not-B' : TermsQuery('A & ~B'),
    'X-and-Y' : TermsQuery('X & Y')
}

docs = [
    'A is the first letter of ...',
    'A and B letters, X and Y letters'
]

for doc in docs:
    words = doc.split()
    doc_tags = [name for (name, query) in tags.items() if query(words)]
    print(doc, doc_tags)
```
