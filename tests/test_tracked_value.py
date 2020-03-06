from query_diet.core import TrackedValue


def test_updating_non_existing_value():
    tv = TrackedValue([])
    tv["field#1"] = 1, 1, 1, 1

    assert tv["field#1"] == (1, 1, 1, 1)


def test_not_overwriting_existing_value():
    tv = TrackedValue(["field#1"])

    assert tv["field#1"] == (0, 0, 0, 0)

    tv["field#1"] = 1, 1, 1, 0
    assert tv["field#1"] == (1, 1, 1, 0)

    tv["field#1"] = 1, 0, 0, 0
    assert tv["field#1"] == (1, 1, 1, 0)
