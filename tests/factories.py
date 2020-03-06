import factory

from tests.project.example import models


class OrganizationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Organization

    name = factory.Sequence(lambda n: "org#%d" % n)


class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Account

    name = factory.Sequence(lambda n: "account#%d" % n)
    org = factory.SubFactory(OrganizationFactory)
