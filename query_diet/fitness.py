from contextlib import contextmanager

from query_diet import context
from query_diet.utils import NOT_PROVIDED, _assert_fitness


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
    raise NotImplementedError
