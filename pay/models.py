from django.db import models

from core.models  import TimeStampModel
from coupons.models import Coupon
from users.models import User, Card

class Payment(TimeStampModel):
    merchant_uid = models.CharField(max_length=250, unique=True)
    imp_uid = models.CharField(max_length=250, null=True)
    status = models.CharField(max_length=250) # ready, paid, failed, cancelled 중 하나
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    class Meta:
        db_table = 'payments'

class Order(TimeStampModel):
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=250) # pending(결제 완료 전), paid, failed, cancelled 중 하나
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=3, max_digits=10)
    actual_amount = models.DecimalField(decimal_places=3, max_digits=10)
    name = models.CharField(max_length=200) # 선불금충전, 선불금사용, 후불결제, 바로결제 중 하나
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = 'orders'