import subprocess

import pytest

from query_diet import __version__
from tests.project.example.models import Account, Organization


def test_version():
    python_version = f"query-diet {__version__}"
    poetry_version = subprocess.run(["poetry", "version"], stdout=subprocess.PIPE).stdout.decode("utf-8").rstrip()
    assert python_version == poetry_version


@pytest.mark.django_db
def test_seed_success(seed):
    assert Organization.objects.count()
    assert Account.objects.count()
