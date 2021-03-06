import pandas as pd

from query_diet import utils


class BaseData:
    __slots__ = ["df"]

    def __init__(self, df):
        self.df = df


class Usage(BaseData):
    def _group(self, *columns):
        grouped = self.df.groupby(list(columns)).agg({"field": "count", "used": "sum"})
        grouped_percent = utils.humanize(100 * (1 - (grouped.field - grouped.used) / grouped.field))
        return grouped_percent

    @property
    def queries(self):
        group = self._group("query")
        return group.to_dict()

    @property
    def models(self):
        group = self._group("model")
        return group.to_dict()

    @property
    def instances(self):
        group = self._group("model", "pk")
        return group.to_dict()

    @property
    def fields(self):
        group = self._group("model", "field")
        return group.to_dict()

    @property
    def total(self):
        total = self.df.agg({"field": "count", "used": "sum"})
        total_percent = utils.humanize(100 * total.used / total.field)
        return total_percent

    @property
    def as_dict(self):
        return {
            "queries": self.queries,
            "models": self.models,
            "instances": self.instances,
            "fields": self.fields,
            "total": self.total,
        }


class Count(BaseData):
    @property
    def queries(self):
        return self.df["query"].nunique()

    @property
    def models(self):
        return self.df["model"].nunique()

    @property
    def instances(self):
        return self.df.groupby(["model", "pk"])["pk"].nunique().sum()

    @property
    def fields(self):
        return self.df.groupby(["model", "field"])["field"].nunique().sum()

    @property
    def as_dict(self):
        return {
            "queries": self.queries,
            "models": self.models,
            "instances": self.instances,
            "fields": self.fields,
        }


class N1(BaseData):
    @property
    def total(self):
        return self.df["n1"].sum()

    @property
    def as_dict(self):
        return {
            "total": self.total,
        }


class Analyzer:
    __slots__ = ["df", "usage", "count", "n1"]

    def __init__(self, data):
        self.df = utils.construct_fields_frame(data)
        self.usage = Usage(self.df)
        self.count = Count(self.df)
        self.n1 = N1(self.df)

    @property
    def analysis(self):
        return {"usage": self.usage.as_dict, "n1": self.n1.as_dict, "count": self.count.as_dict}
