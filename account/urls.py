from django.urls import path
from account.views import verify_otp, add_to_cart, show_cart, remove_cart_item, payment_success, register, login, logout, change_password, forgot_password, reset_password, check_token

urlpatterns = [
    
    path('add_to_cart/<product_uid>', add_to_cart, name='add_to_cart'),
    path('cart', show_cart, name='show_cart'),
    path('remove_cart_item/<cart_item_uid>', remove_cart_item, name='remove_cart_item'),
    path('payment_success', payment_success, name='payment_success'),
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
    path('change_password', change_password, name='change_password'),
    path('forgot_password', forgot_password, name='forgot_password'),
    path('check_token/<reset_token>', check_token, name='check_token'),
    path('reset_password/<reset_token>', reset_password, name='reset_password'),
    path('verify_otp/<user_id>', verify_otp, name='verify_otp'),
]
