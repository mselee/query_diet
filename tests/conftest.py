import pytest

from tests.project.example.models import Account, Organization


@pytest.fixture(scope="session")
def seed(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        for _ in range(10):
            org = Organization.objects.create()
            for _ in range(3):
                org.accounts.create()
