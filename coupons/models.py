from django.db import models
from datetime import datetime 

class Coupon(models.Model):
    name = models.CharField(max_length=200)
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField()

    class Meta:
        db_table = 'coupons'