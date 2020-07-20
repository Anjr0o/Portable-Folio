from django.contrib import admin

# Register your models here.
from .models import Stock, Balance, Transaction

admin.site.register(Stock)
admin.site.register(Balance)
admin.site.register(Transaction)