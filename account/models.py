from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from product.models import Product, Category, SizeVariant
from uuid import uuid4

# Create your models here.

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='profile_images')
    is_active = models.BooleanField(default=False)
    is_otp_verified = models.BooleanField(default=False)
    pwd_reset_token = models.CharField(max_length=255, blank=True, null=True)
    otp = models.CharField(max_length=255, blank=True, null=True)

    def get_reset_password_token(self):
        reset_token = str(uuid4())
        self.pwd_reset_token = reset_token
        self.save()
        return reset_token

    def get_cart_count(self):
        return CartItem.objects.filter(cart__user=self.user, cart__is_paid=False).count()

    def __str__(self):
        return f'{self.user.username} - {self.phone} - {self.address} - {self.avatar} - {self.is_active} - {self.is_otp_verified}'

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_signature = models.CharField(max_length=255, blank=True, null=True)

    def get_total_price(self):
        total_price = 0
        for item in self.cart_items.all():
            print(f'items ******* {item}')
            total_price += (item.product.price + item.size_variant.price) * (item.quantity)
        return total_price

    def __str__(self):
        return f'{self.user.username} - {self.total_price} - {self.is_paid} - {self.is_delivered}'
    

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE, null=True, blank=True)

    def get_item_total_price(self):
        return (self.product.price + self.size_variant.price) * self.quantity

    def __str__(self):
        return f'{self.product.name} - {self.size_variant.price} - {self.price} - {self.quantity}'
    

