import pytest

from query_diet import __version__
from tests.project.example.models import Account, Organization


def test_version():
    assert __version__ == "0.1.1"


@pytest.mark.django_db
def test_seed_success(seed):
    assert Organization.objects.count()
    assert Account.objects.count()
