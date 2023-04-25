from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # name = models.CharField(max_length=20)
    # password = models.CharField(max_length=20)
    balance = models.FloatField()
    pin = models.CharField(max_length=100)

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    amount = models.FloatField()
    balance = models.FloatField()
    date = models.CharField(max_length=20)
    to = models.CharField(max_length=20)
    fro = models.CharField(max_length=20)
