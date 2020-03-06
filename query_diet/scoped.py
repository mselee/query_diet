from contextlib import contextmanager

from query_diet.utils import NOT_PROVIDED


class ScopedContextVar:
    def __init__(self, var, *, factory=NOT_PROVIDED):
        self.var = var
        self.factory = factory

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.var, name)

    @contextmanager
    def scoped(self, value=NOT_PROVIDED):
        if value is NOT_PROVIDED:
            value = self.factory() if self.factory is not NOT_PROVIDED else self.var.get()
        token = self.var.set(value)
        try:
            yield value
        finally:
            self.var.reset(token)

    def __call__(self):
        try:
            return self.var.get()
        except LookupError:
            return self.var.get(None)
