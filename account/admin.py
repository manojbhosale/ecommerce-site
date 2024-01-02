from django.contrib import admin
# Register your models here.

from .models import UserProfile, Cart, CartItem

admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)

