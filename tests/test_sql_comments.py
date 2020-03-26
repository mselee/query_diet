import pytest
from django.db.models import Count

from query_diet import context
from tests.project.example.models import Organization


@pytest.mark.django_db
def test_select():
    with context.tracker.scoped() as tracker:
        list(Organization.objects.all().comment("tag:100"))
    sql = tracker.queries[0]
    assert "/*tag:100*/" in sql


@pytest.mark.django_db
def test_update():
    with context.tracker.scoped() as tracker:
        Organization.objects.all().comment("tag:101").update(name="monty")
    sql = tracker.queries[0]
    assert "/*tag:101*/" in sql


@pytest.mark.django_db
def test_delete():
    with context.tracker.scoped() as tracker:
        Organization.objects.filter(name="does_not_exist").comment("tag:102").delete()
    sql = tracker.queries[0]
    assert "/*tag:102*/" in sql


@pytest.mark.django_db
def test_select_aggregate():
    with context.tracker.scoped() as tracker:
        Organization.objects.all().comment("tag:103").aggregate(Count("name"))
    sql = tracker.queries[0]
    assert "/*tag:103*/" in sql


@pytest.mark.django_db
def test_chained():
    with context.tracker.scoped() as tracker:
        list(Organization.objects.all().comment("tag:100", "app:01").comment("served:yes"))
    sql = tracker.queries[0]
    assert "/*tag:100*/\n/*app:01*/\n/*served:yes*/" in sql


@pytest.mark.django_db
def test_combined():
    with context.tracker.scoped() as tracker:
        list(Organization.objects.all().comment("tag:100", "app:01").comment("served:yes", multi=False))
    sql = tracker.queries[0]
    assert "/*tag:100*/\n/*app:01*/\n--served:yes\n" in sql


@pytest.mark.django_db
def test_invalid_tokens():
    with pytest.raises(SyntaxError):
        list(Organization.objects.all().comment("tag:100\napp:01", multi=False))
    list(Organization.objects.all().comment("tag:100\napp:01"))

    with pytest.raises(SyntaxError):
        list(Organization.objects.all().comment("tag:100*/app:01"))
    list(Organization.objects.all().comment("tag:100*/app:01", multi=False))
