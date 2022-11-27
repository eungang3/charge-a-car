from django.db import models

from core.models  import TimeStampModel
from coupons.models import Coupon

class User(TimeStampModel):
    email = models.CharField(max_length=250, unique=True)
    password = models.CharField(max_length=250)
    balance = models.DecimalField(decimal_places=3, max_digits=10, default=0)
    coupons = models.ManyToManyField(Coupon, through='UserCoupon')

    class Meta:
        db_table = 'users'

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_coupons'

class Card(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_uid = models.CharField(max_length=250, unique=True)
    pay_day = models.IntegerField(null=True)
    class Meta:
        db_table = 'cards'
