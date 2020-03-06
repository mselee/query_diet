import shortuuid
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
    if data.get(field_name, self) is self:
        # Let's see if the field is part of the parent chain. If so we
        # might be able to reuse the already loaded value. Refs #18343.
        val = self._check_parent_chain(instance)
        if val is None:
            instance.refresh_from_db(fields=[field_name])
            val = getattr(instance, field_name)

            if tracker := context.tracker():
                tracker.track_access(
                    instance.__class__, instance.pk, field_name, instance.query_id, lazy=True,
                )
        data[field_name] = val
    else:
        if tracker := context.tracker():
            tracker.track_access(instance.__class__, instance.pk, field_name, instance.query_id)
    return data[field_name]


# Lazy-loaded relations

old_des_get = ForwardManyToOneDescriptor.__get__


def new_des_get(self, instance, cls=None):
    if instance is None:
        return self

    lazy = not self.field.is_cached(instance)
    ret = old_des_get(self, instance, cls=cls)

    if tracker := context.tracker():
        tracker.track_access(
            instance.__class__, instance.pk, self.field.name, instance.query_id, lazy=lazy,
        )
    return ret


# Tag the active query

old_fetch_all = models.QuerySet._fetch_all


def new_fetch_all(self):
    tracker = context.tracker()
    if not tracker:
        old_fetch_all(self)
        return

    query_id = shortuuid.uuid()

    self.comment(f"{context.query_prefix()}:query_id:{query_id}")

    with context.query_id.scoped(query_id):
        old_fetch_all(self)


# Track field access

old_getter = models.Model.__getattribute__


def __getattribute__(self, name):
    try:
        fields = old_getter(self, "query_fields")
        if name in fields and (tracker := context.tracker()):
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

    if (tracker := context.tracker()) and (query_id := context.query_id()):
        tracker.track_instance(cls, instance, query_id, field_names)

    return instance


# Unleash the monkey


def patch():
    ForwardManyToOneDescriptor.__get__ = new_des_get
    if context.is_strict_columns_enabled():
        DeferredAttribute.__get__ = new_get
    else:
        ForeignKeyDeferredAttribute.__get__ = new_get
    models.QuerySet._fetch_all = new_fetch_all
    setattr(models.Model, "__getattribute__", __getattribute__)
    setattr(models.Model, "from_db", new_from_db)
    comment.patch()
