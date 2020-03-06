from query_diet import analyzer, utils


class TrackedValue:
    __slots__ = ["fields"]

    def __init__(self, fields):
        _fields = {}
        for f in fields:
            # used, lazy, deferred, n+1
            _fields[f] = 0, 0, 0, 0
        self.fields = _fields

    def __getitem__(self, key):
        return self.fields[key]

    def __setitem__(self, key, new_value):
        try:
            old_used, old_lazy, old_deferred, old_nplusone = self.fields[key]
        except KeyError:
            old_used, old_lazy, old_deferred, old_nplusone = 0, 0, 0, 0
        new_used, new_lazy, new_deferred, new_nplusone = new_value
        self.fields[key] = old_used | new_used, old_lazy | new_lazy, old_deferred | new_deferred, old_nplusone | new_nplusone


class Tracker:
    __slots__ = ["tracked_fields"]

    def __init__(self):
        self.tracked_fields = {}

    def track_instance(self, model, instance, query_id, field_names):
        query_fields = utils.filter_field_names(field_names)
        setattr(instance, "query_id", query_id)
        setattr(instance, "query_fields", query_fields)
        self.tracked_fields[(query_id, model, instance.pk)] = TrackedValue(query_fields)

    def track_access(self, model, pk, field_name, query_id, lazy=False):
        key = (query_id, model, pk)
        used = 1
        deferred = int(self.is_deferred_violation(model, pk)) if lazy else 0
        nplusone = int(self.is_nplusone_relation(query_id, model, pk, field_name)) if lazy else 0
        self.tracked_fields[key][field_name] = used, lazy, deferred, nplusone

    def is_deferred_violation(self, model, pk):
        for _, _model, _pk in self.tracked_fields.keys():
            if _model == model and _pk == pk:
                return True
        return False

    def is_nplusone_relation(self, query, model, pk, field):
        try:
            for _query, _model, _pk in self.tracked_fields.keys():
                if _query == query and _model == model and _pk != pk:
                    used, lazy, deferred, nplusone = self.tracked_fields[_query, _model, _pk][field]
                    return bool(lazy) or bool(nplusone)
        except KeyError:
            pass
        return False

    def is_nplusone_column(self):
        raise NotImplementedError

    def analyze(self):
        return analyzer.Analyzer(self.tracked_fields) if self.tracked_fields else None

    @property
    def diag(self):
        queries, models, pks = list(zip(*self.tracked_fields.keys()))
        return set(queries), set(models), set(pks)
