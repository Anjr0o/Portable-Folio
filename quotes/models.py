from django.db import models

# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.ticker

class Balance(models.Model):
    title = models.CharField(default='Balance', max_length=10)
    amount = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return self.title
