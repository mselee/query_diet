from unittest.mock import MagicMock

from query_diet.analyzer import Analyzer


def test_basic_metrics():
    data = {
        ("query#1", "model#1", "instance#1"): MagicMock(fields={"field#1.1": (0, 0, 0, 0), "field#1.2": (0, 0, 0, 0)}),
        ("query#2", "model#1", "instance#2"): MagicMock(fields={"field#1.1": (1, 0, 0, 0), "field#1.2": (0, 0, 0, 0)}),
        ("query#1", "model#2", "instance#1"): MagicMock(fields={"field#2.1": (0, 0, 0, 0), "field#2.2": (1, 0, 0, 0)}),
        ("query#2", "model#2", "instance#2"): MagicMock(fields={"field#2.1": (1, 0, 0, 0), "field#2.2": (1, 0, 0, 0)}),
    }
    analyzer = Analyzer(data)
    metrics = analyzer.analysis

    usage = {
        "queries": {"query#1": 25.0, "query#2": 75.0},
        "models": {"model#1": 25.0, "model#2": 75.0},
        "instances": {
            ("model#1", "instance#1"): 0.0,
            ("model#1", "instance#2"): 50.0,
            ("model#2", "instance#1"): 50.0,
            ("model#2", "instance#2"): 100.0,
        },
        "fields": {
            ("model#1", "field#1.1"): 50.0,
            ("model#1", "field#1.2"): 0.0,
            ("model#2", "field#2.1"): 50.0,
            ("model#2", "field#2.2"): 100.0,
        },
        "total": 50.0,
    }
    assert metrics["usage"]["queries"] == usage["queries"]
    assert metrics["usage"]["models"] == usage["models"]
    assert metrics["usage"]["instances"] == usage["instances"]
    assert metrics["usage"]["fields"] == usage["fields"]
    assert metrics["usage"]["total"] == usage["total"]
