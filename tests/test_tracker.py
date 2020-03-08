import pytest

from query_diet import assert_fitness, context
from tests.factories import AccountFactory
from tests.project.example.models import Account, Organization


@pytest.fixture()
def accounts_pks(db):
    return [account.pk for account in AccountFactory.create_batch(10)]


@pytest.mark.django_db
def test_nplusone_triggered(accounts_pks):
    with context.tracker.scoped() as tracker:
        accounts = list(Account.objects.select_related(None).filter(pk__in=accounts_pks))

        for account in accounts:
            name = account.org.name

        assert tracker.analyze().n1.total == len(accounts) - 1


@assert_fitness(usage=0)
@pytest.mark.django_db
def test_nplusone_not_triggered(accounts_pks):
    accounts = list(Account.objects.select_related("org").filter(pk__in=accounts_pks))

    for account in accounts:
        name = account.org.name
