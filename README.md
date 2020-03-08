![](https://github.com/mselee/query_diet/workflows/Tests/badge.svg)

# query_diet

[query_diet](https://github.com/seleem1337/query_diet) is a package that tracks queries made by the Django ORM. Currently, it tries to detect:

1. Lazy-loaded database relations.
2. Columns that are fetched but are never used.
3. Deferred columns that could have been loaded eagerly.
4. Basic N+1 queries (forward relations that can be solved via `select_related`).

**NOTE: this should be used for development/testing/CI setups only.**

## Why

The default behavior of the ORM makes it easy to have very fat queries that are inefficient.

## Why not

Allergy to monkey-patching.

## Support

- Python 3.6.1+
- Django 3.0+

## Installation

```console
$ poetry add --dev query_diet
```

## Configuration

```python
# settings.py

# defaults
QUERY_DIET_STRICT_RELATIONS=True
QUERY_DIET_STRICT_COLUMNS=True
QUERY_DIET_MACHINE_PREFIX=platform.node
QUERY_DIET_USAGE_THRESHOLD=0
QUERY_DIET_N1_THRESHOLD=0

if DEBUG:
    from query_diet import monkey

    monkey.patch()

    # optional
    MIDDLEWARE.append('query_diet.middleware.TrackerMiddleware')
```

[query_diet](https://github.com/seleem1337/query_diet) relies heavily on [contextvars](https://docs.python.org/3.7/library/contextvars.html) which means you can override the configuration at any execution point:

```python
from query_diet import context

with context.query_prefix.scoped("appserver-01"):
    do_stuff()

```

### Examples

Unused columns:

```python
import pytest
from query_diet import assert_fitness

# asserts that the column(s) usage % is >= 80
@assert_fitness(usage=80)
@pytest.mark.django_db
def test_query_fitness():
    wonderful_big_fat_queries()
```

N+1 relations:

```python
import pytest
from query_diet import assert_fitness

# asserts that the no. of N+1 violations is <= 0
@assert_fitness(n1=0)
@pytest.mark.django_db
def test_query_fitness():
    wonderful_big_fat_queries()
```

Queries count:

```python
import pytest
from query_diet import assert_fitness

# asserts that the no. of queries is <= 11
@assert_fitness(query_count=11)
@pytest.mark.django_db
def test_query_fitness():
    wonderful_big_fat_queries()
```

Assertion hooks:

```python
import pytest
from query_diet import assert_fitness

from myapp.models import Foo

def _clear_caches(tracker):
    pass

def _custom_assert(analyzer):
    assert analyzer.usage.models[Foo] == 100

# `pre` hooks are executed before the test is executed.
# `post` hooks are executed after the built-in assertions (e.g. usage, n1, query_count) are executed.
@assert_fitness(usage=80, pre=[_clear_caches], post=[_custom_assert])
@pytest.mark.django_db
def test_query_fitness():
    wonderful_big_fat_queries()
```

Assertion range:

```python
@assert_fitness(query_count=[4, 7])
@pytest.mark.django_db
def test_query_fitness():
    wonderful_big_fat_queries()
```

You can also assert the data manually:

```python
import pytest
from query_diet import context

from myapp.models import Foo

@pytest.mark.django_db
def test_query_fitness():
    with context.tracker.scoped() as tracker:
        wonderful_big_fat_queries()

        analyzer = tracker.analyze()

        assert analyzer.usage.total >= 80.0
        assert analyzer.analysis["usage"]["models"][Foo] >= 80.0
```

## Guide

### Explicit

```python
from query_diet import context

def endpoint():
    execute_order_65()

    with context.tracker.scoped() as tracker:
        execute_order_66()
        print(tracker.analyze().analysis)

    execute_order_67()
```

### Middleware

There are two signals you can listen to:

- `pre_track` is fired before the request is tracked, but after a tracker instance is constructed.
- `post_track` is fired after the tracking is completed (i.e. after the request has finished processing).

Both `pre_track` and `post_track` handlers accept the same arguments:

- `sender` which is the middleware class.
- `tracker` which is the tracker instance associated with the current scope (i.e. request).

```python
from query_diet.middleware import post_track

def post_track_handler(sender, tracker):
    send_metrics_to_dev_null(tracker.analyze().analysis)

post_track.connect(post_track_handler)
```

### Tags

A unique query id is generated for every query. This id is included in the query in the form of a SQL comment.

This is useful for cross-referencing database query logs against application requests.

### Analyzer

`tracker.analyze()` returns an instance of the `Analyzer` class. It converts the tracked data into a pandas dataframe:

```python
analyzer = tracker.analyze()
df = analyzer.df
```

You can then compute different metrics about your queries. There's also some basic metrics available via `analyzer.analysis`:

```python
{
    "usage": {
        "queries": {
            # usage percent grouped by query id
            139748783266864: 25.0,
            139748783264160: 75.0
        },
        "models": {
            # usage percent grouped by model class
            <class '__main__.Foo'>: 25.0,
            <class '__main__.Bar'>: 75.0
        }
        "instances": {
            # usage percent grouped by model class and instance pk
            (<class '__main__.Foo'>, 197): 0.0,
            (<class '__main__.Foo'>, 198): 50.0,
            (<class '__main__.Bar'>, 225): 50.0,
            (<class '__main__.Bar'>, 226): 100.0,
        },
        "fields": {
            # usage percent grouped by model class and field name
            (<class '__main__.Foo'>, "name"): 50.0,
            (<class '__main__.Foo'>, "desc"): 0.0,
            (<class '__main__.Bar'>, "capacity"): 50.0,
            (<class '__main__.Bar'>, "price"): 100.0,
        },
        # total usage percent
        "total": 50.0,
    },
    "count": {
        "queries": 2,
        "models": 2,
        "instances": 4,
        "fields": 4
    },
    "n1": {
        "total: 0
    }
}
```
