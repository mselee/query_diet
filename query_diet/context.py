from contextvars import ContextVar

from query_diet import core, defaults
from query_diet.scoped import ScopedContextVar

# core

__tracker = ContextVar("tracker")
__query_id = ContextVar("query_id")
__query_fields = ContextVar("query_fields")
__ignored = ContextVar("ignore")

tracker = ScopedContextVar(__tracker, factory=core.Tracker)
query_id = ScopedContextVar(__query_id)
query_fields = ScopedContextVar(__query_fields)
ignored = ScopedContextVar(__ignored)

# config

__is_strict_relations_enabled = ContextVar("strict_relations", default=defaults.is_strict_relations_enabled)
__is_strict_columns_enabled = ContextVar("strict_columns", default=defaults.is_strict_columns_enabled)
__query_prefix = ContextVar("query_prefix", default=defaults.query_prefix)

is_strict_relations_enabled = ScopedContextVar(__is_strict_relations_enabled)
is_strict_columns_enabled = ScopedContextVar(__is_strict_columns_enabled)
query_prefix = ScopedContextVar(__query_prefix)

# assertions
__usage_threshold = ContextVar("usage_threshold", default=defaults.usage_threshold)
__n1_threshold = ContextVar("n1_threshold", default=defaults.n1_threshold)

usage_threshold = ScopedContextVar(__usage_threshold)
n1_threshold = ScopedContextVar(__n1_threshold)
