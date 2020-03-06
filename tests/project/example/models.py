from django.db import models


class Organization(models.Model):
    name = models.TextField()
    yesno = models.BooleanField(default=False)


class Account(models.Model):
    name = models.TextField()
    yesno = models.BooleanField(default=False)
    org = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="accounts")
