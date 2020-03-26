import re

import pandas as pd

from query_diet import context


class NOT_PROVIDED:
    pass


def humanize(value):
    return round(value, 2)


def filter_field_names(field_names):
    return set(name for name in field_names if not name == "id" and not name.endswith("_id"))


def construct_fields_frame(data):
    processed_data = [(*k, tuple([(k1,) + v1 for k1, v1 in data[k].fields.items()])) for k, v in data.items()]
    df = pd.DataFrame.from_records(processed_data)
    df.columns = ["query", "model", "pk", "field"]
    df = df.explode("field")
    df[["field", "used", "lazy", "deferred", "n1"]] = pd.DataFrame(df.field.tolist(), index=df.index)
    return df


def export_fields_frame(frame):
    df = frame.copy()
    df.model = df.model.apply(lambda c: f"{c.__module__}.{c.__name__}")
    df.to_sql(name="fields", con=context.db, if_exists="append", method="multi")


def construct_queries_frame(data):
    regex = re.compile(r"\/\*(.*:.*)\*\/")
    processed_data = []
    for query in data:
        matches = re.findall(regex, query)
        if not matches:
            continue
        entry = {"sql": query}
        for match in matches:
            key, value = match.split(":")
            entry[key] = value
        processed_data.append(entry)

    df = pd.DataFrame.from_records(processed_data)
    return df


def export_queries_frame(frame):
    df = frame.copy()
    df.to_sql(name="queries", con=context.db, if_exists="append", method="multi")
