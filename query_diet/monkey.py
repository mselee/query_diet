import inspect
import sys

from django.db import models
from django.db.models.fields.related_descriptors import ForeignKeyDeferredAttribute, ForwardManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute

from query_diet import comment, context, utils

# Deferred columns

old_rel_get = ForeignKeyDeferredAttribute.__get__
old_col_get = DeferredAttribute.__get__


def new_get(self, instance, cls=None):
    if instance is None:
        return self
    data = instance.__dict__
    field_name = self.field.attname
    lazy = False
    if data.get(field_name, self) is self:
        # Let's see if the field is part of the parent chain. If so we
        # might be able to reuse the already loaded value. Refs #18343.
        val = self._check_parent_chain(instance)
        if val is None:
            instance.refresh_from_db(fields=[field_name])
            val = getattr(instance, field_name)
            lazy = True
        data[field_name] = val

    tracker = context.tracker()
    if tracker:
        tracker.track_access(
            instance.__class__, instance.pk, field_name, instance.query_id, lazy=lazy,
        )

    return data[field_name]


# Lazy-loaded relations

old_des_get = ForwardManyToOneDescriptor.__get__


def new_des_get(self, instance, cls=None):
    if instance is None:
        return self

    lazy = not self.field.is_cached(instance)
    ret = old_des_get(self, instance, cls=cls)

    tracker = context.tracker()
    if tracker:
        tracker.track_access(
            instance.__class__, instance.pk, self.field.name, instance.query_id, lazy=lazy,
        )
    return ret


# Decorator for tagging the active query


def tag_query(func):
    def wrapped(self, *args, **kwargs):
        tracker = context.tracker()
        if not tracker:
            func(self, *args, **kwargs)
            return

        frame = sys._getframe()
        while True:
            frame = frame.f_back
            module = inspect.getmodule(frame).__spec__.name
            if not module.startswith("django"):
                caller = frame.f_code.co_name
                line = frame.f_lineno
                caller_self = frame.f_locals.get("self", None)
                klass = caller_self.__class__.__name__ if caller_self is not None else "N/A"
                break

        query_prefix = str(context.query_prefix()())
        query_id = str(context.query_tagger()())
        query_module = f"module:{module}"
        query_class = f"class:{klass}"
        query_func = f"func:{caller}"
        query_line = f"line:{line}"

        self.tag(f"query_prefix:{query_prefix}", f"query_id:{query_id}", query_module, query_class, query_func, query_line)

        with context.query_id.scoped(query_id):
            tracker.track_query(str(self.query))
            return func(self, *args, **kwargs)

    return wrapped


# Track field access

old_getter = models.Model.__getattribute__


def __getattribute__(self, name):
    try:
        fields = old_getter(self, "query_fields")
        if name in fields:
            tracker = context.tracker()
            if tracker:
                model = old_getter(self, "__class__")
                pk = old_getter(self, "pk")
                query_id = old_getter(self, "query_id")

                tracker.track_access(model, pk, name, query_id)
    except AttributeError:
        pass

    return old_getter(self, name)


# Track model fetching

old_from_db = models.Model.from_db.__func__  # `__func__` because `from_db` is decorated


@classmethod
def new_from_db(cls, db, field_names, values):
    instance = old_from_db(cls, db, field_names, values)

    tracker = context.tracker()
    if tracker:
        query_id = context.query_id()
        if query_id:
            tracker.track_instance(cls, instance, query_id, field_names)

    return instance


# Unleash the monkey


def patch():
    ForwardManyToOneDescriptor.__get__ = new_des_get
    if context.is_strict_columns_enabled():
        DeferredAttribute.__get__ = new_get
    else:
        ForeignKeyDeferredAttribute.__get__ = new_get
    models.QuerySet._fetch_all = tag_query(models.QuerySet._fetch_all)
    models.QuerySet.update = tag_query(models.QuerySet.update)
    models.QuerySet.aggregate = tag_query(models.QuerySet.aggregate)
    models.QuerySet.delete = tag_query(models.QuerySet.delete)
    setattr(models.Model, "__getattribute__", __getattribute__)
    setattr(models.Model, "from_db", new_from_db)
    comment.patch()
