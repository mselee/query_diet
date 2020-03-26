import inspect

from django.db.models import query, sql
from django.db.models.sql import compiler


def add_comment_to_sql(sql, params, comment):
    return f"{comment}{sql}", params


class CompilerMixin:
    def get_comment_sql(self):
        comments = []
        for comment, multi in self.query.comments:
            if multi:
                if "*/" in comment:
                    raise SyntaxError
                comment = "/*%s*/" % comment
            else:
                if "\n" in comment:
                    raise SyntaxError
                comment = "--%s\n" % comment
            comments.append(comment)
        sql = "\n".join(comments)
        if sql and not sql.endswith("\n"):
            sql += "\n"
        return sql

    def as_sql(self, *args, **kwargs):
        result = super().as_sql(*args, **kwargs)

        comment = self.get_comment_sql()
        if isinstance(result, list):
            result = [add_comment_to_sql(sql, params, comment) for sql, params in result]
        else:
            sql, params = result
            result = add_comment_to_sql(sql, params, comment)

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


def tag(self, *comments, multi=True):
    """
    Mutates the current QuerySet with `comments` added to query as SQL comments.
    """
    self.query.comments += [(c, multi) for c in comments]
    return self


def comment(self, *comments, multi=True):
    """
    Return a new QuerySet with `comments` added to query as SQL comments.
    """
    clone = self._chain()
    clone.query.comments += [(c, multi) for c in comments]
    return clone


# ******************************
# Hacks
# ******************************


def patch():
    query.QuerySet.tag = tag
    query.QuerySet.comment = comment
    sql.Query = Query
    sql.UpdateQuery.__bases__ = (sql.Query,)
    sql.AggregateQuery.__bases__ = (sql.Query,)
    compiler.SQLCompiler = SQLCompiler
    compiler.SQLUpdateCompiler = SQLUpdateCompiler
    compiler.SQLAggregateCompiler = SQLAggregateCompiler
