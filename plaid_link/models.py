from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    item_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Account(models.Model):
    account_id = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    balance_available = models.FloatField(default=None, null=True)
    balance_current = models.FloatField()


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=100)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateField()
    name = models.CharField(max_length=100)
    pending = models.BooleanField()
