import pytest

from query_diet import assert_fitness, context
from tests.factories import OrganizationFactory
from tests.project.example.models import Organization


@pytest.fixture(scope="function")
def org_pks(db):
    return [org.pk for org in OrganizationFactory.create_batch(10)]


@pytest.mark.django_db
def test_assert_usage_below_threshold():
    with pytest.raises(AssertionError), assert_fitness(usage=100):
        Organization.objects.create()
        org = Organization.objects.first()


@assert_fitness(usage=50)
@pytest.mark.django_db
def test_assert_usage_above_threshold():
    Organization.objects.create()
    org = Organization.objects.first()
    org.name


@assert_fitness(query_count=3)
@pytest.mark.django_db
def test_assert_query_count_below_threshold(org_pks):
    for pk in org_pks[:3]:
        Organization.objects.get(pk=pk)


@pytest.mark.django_db
def test_assert_query_count_above_threshold(org_pks):
    with pytest.raises(AssertionError), assert_fitness(query_count=3):
        for pk in org_pks:
            Organization.objects.get(pk=pk)


@context.usage_threshold.scoped(50.0)
@assert_fitness()
@pytest.mark.django_db
def test_overriding_threshold():
    Organization.objects.create()
    org = Organization.objects.first()
    org.name


@pytest.mark.django_db
def test_context_manager():
    with assert_fitness(usage=100):
        Organization.objects.create()
        org = Organization.objects.first()
        org.name
        org.yesno


def _assert_usage_is_100(analyzer):
    assert analyzer.usage.total == 100


@assert_fitness(post=[_assert_usage_is_100])
@pytest.mark.django_db
def test_custom_assertion():
    Organization.objects.create()
    org = Organization.objects.first()
    org.name
    org.yesno


@assert_fitness(usage=[40, 50])
@pytest.mark.django_db
def test_assertion_usage_range_success():
    Organization.objects.create()
    org = Organization.objects.first()
    org.name


@pytest.mark.django_db
def test_assertion_usage_range_fails():
    with pytest.raises(AssertionError), assert_fitness(usage=[40, 50]):
        Organization.objects.create()
        org = Organization.objects.first()
        org.name
        org.yesno


@assert_fitness(n1=[0, 1])
@pytest.mark.django_db
def test_assertion_n1_range_success():
    Organization.objects.create()
    org = Organization.objects.first()
    org.name


@pytest.mark.django_db
def test_assertion_n1_range_fails():
    with pytest.raises(AssertionError), assert_fitness(n1=[10, 20]):
        Organization.objects.create()
        org = Organization.objects.first()
        org.name
        org.yesno
