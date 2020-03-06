import inspect

from django.db.models import query, sql
from django.db.models.sql import compiler

COMMENT_START = "/*"
COMMENT_END = "*/"


class CompilerMixin:
    def _insert_comments(self, pair):
        comments = self.query.comments
        if not comments:
            return pair

        sql, params = pair
        lines = [f"{COMMENT_START} {c} {COMMENT_END}" for c in comments]
        lines.append(sql)
        sql = " ".join(lines)
        return sql, params

    def as_sql(self, *args, **kwargs):
        result = super().as_sql(*args, **kwargs)

        if isinstance(result, list):
            result = [self._insert_comments(pair) for pair in result]
        else:
            result = self._insert_comments(result)

        return result


class SQLCompiler(CompilerMixin, compiler.SQLCompiler):
    pass


class SQLUpdateCompiler(CompilerMixin, compiler.SQLUpdateCompiler):
    pass


class SQLAggregateCompiler(CompilerMixin, compiler.SQLAggregateCompiler):
    pass


class Query(sql.Query):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comments = []

    def clone(self):
        obj = super().clone()
        obj.comments = self.comments.copy()
        return obj


def comment(self, *comments):
    for c in comments:
        assert isinstance(c, str), "comments must be strings."
        assert COMMENT_START not in c, f"'{COMMENT_START}' is not allowed in comment blocks."
        assert COMMENT_END not in c, f"'{COMMENT_END}' is not allowed in comment blocks."

    self.query.comments += comments
    return self


# ******************************
# Hacks
# ******************************


def patch():
    query.QuerySet.comment = comment
    sql.Query = Query
    sql.UpdateQuery.__bases__ = (sql.Query,)
    sql.AggregateQuery.__bases__ = (sql.Query,)
    compiler.SQLCompiler = SQLCompiler
    compiler.SQLUpdateCompiler = SQLUpdateCompiler
    compiler.SQLAggregateCompiler = SQLAggregateCompiler
