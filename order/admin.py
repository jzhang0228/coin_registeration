from django.contrib import admin
from .models import UserInformation, OrderDetail, Business

admin.site.register(Business)
admin.site.register(UserInformation)
admin.site.register(OrderDetail)