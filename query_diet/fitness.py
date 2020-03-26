from contextlib import contextmanager

from query_diet import context, utils
from query_diet.utils import NOT_PROVIDED


def _assert_fitness(analyzer, usage, n1, query_count):
    if isinstance(usage, (list, tuple)):
        min_usage, max_usage = usage
        assert (
            min_usage <= analyzer.usage.total <= max_usage
        ), f"Expected query usage to be >= {min_usage} and <= {max_usage} but got {analyzer.usage.total} instead."
    else:
        assert analyzer.usage.total >= usage, f"Expected query usage to be >= {usage} but got {analyzer.usage.total} instead."

    if isinstance(n1, (list, tuple)):
        min_n1, max_n1 = n1
        assert (
            min_n1 <= analyzer.n1.total <= max_n1
        ), f"Expected N+1 queries to be >= {min_n1} and <= {max_n1} but got {analyzer.n1.total} instead."
    else:
        assert analyzer.n1.total <= n1, f"Expected N+1 queries to be <= {n1} but got {analyzer.n1.total} instead."

    if query_count is not NOT_PROVIDED:
        if isinstance(query_count, (list, tuple)):
            min_count, max_count = query_count
            assert (
                min_count <= analyzer.count.queries <= max_count
            ), f"Expected query count to be >= {min_count} and <= {max_count} but got {analyzer.count.queries} instead."
        else:
            assert (
                analyzer.count.queries <= query_count
            ), f"Expected query count to be <= {query_count} but got {analyzer.count.queries} instead."


@contextmanager
def assert_fitness(*, usage=NOT_PROVIDED, n1=NOT_PROVIDED, query_count=NOT_PROVIDED, pre=None, post=None):
    if usage is NOT_PROVIDED:
        usage = context.usage_threshold()
    if n1 is NOT_PROVIDED:
        n1 = context.n1_threshold()

    with context.tracker.scoped() as tracker:
        if pre:
            for hook in pre:
                hook(tracker)
        try:
            yield
        finally:
            analyzer = tracker.analyze()
            if not analyzer:
                return
            _assert_fitness(tracker.analyze(), usage, n1, query_count)
            if post:
                for hook in post:
                    hook(analyzer)


@contextmanager
def track_fitness():
    with context.tracker.get_or_create() as tracker:
        try:
            yield
        finally:
            if tracker.fields:
                frame = utils.construct_fields_frame(tracker.fields)
                utils.export_fields_frame(frame)
            if tracker.queries:
                frame = utils.construct_queries_frame(tracker.queries)
                utils.export_queries_frame(frame)
