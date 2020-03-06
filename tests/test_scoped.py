import uuid
from contextvars import ContextVar

from query_diet.scoped import ScopedContextVar

default_uuid = uuid.uuid4()

__var = ContextVar("var", default=default_uuid)

var = ScopedContextVar(__var, factory=uuid.uuid4)
var_without_factory = ScopedContextVar(__var)


def test_factory():
    with var.scoped() as scoped_var:
        assert isinstance(scoped_var, uuid.UUID)


def test_default():
    with var_without_factory.scoped() as scoped_var:
        assert scoped_var is default_uuid


def test_nested_scopes():
    with var.scoped() as var1, var.scoped() as var2:
        assert var1 is not var2


def test_nested_scopes_shared_context_var():
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    with var.scoped(id1) as var1, var_without_factory.scoped(id2) as var2:
        assert var.var is var_without_factory.var
        assert var1 is not var2
        assert var1 is id1
        assert var2 is id2
