from django.contrib import admin
from .models import Order, Payment 

admin.site.register(Payment)
admin.site.register(Order)