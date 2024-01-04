from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from product.models import Product, SizeVariant
from account.models import CartItem, Cart, User, UserProfile
from django.http import HttpResponseRedirect, HttpResponse
from dotenv import load_dotenv
import os
import razorpay
from base import utils
from random import randint
import logging
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)
# Create your views here.
load_dotenv()


def verify_otp(request, user_id):
    if request.method == "POST":
        otp = request.POST.get('otp')
        # print(f'Email in request session >>>>>>>>> {request.session['email']}')
        user_profile = UserProfile.objects.get(user__email=request.session['email'])
        # print(f'user profile OTP {user_profile.otp} AND request OTP {otp}')
        if user_profile.otp == otp:
            user_profile.is_otp_verified = True
            user_profile.save()
            auth_login(request, user_profile.user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verify_otp', user_id=user_profile.uid)
    # print(f'Email in request session >>>>>>>>> {request.session['email']}')
    return render(request,'account/verify_otp.html')

def check_token(request, reset_token):
    # reset_token = request.GET.get('reset_token')
    profile = UserProfile.objects.get(pwd_reset_token=reset_token)
    if profile:
        return render('reset_password', reset_token=reset_token)
    return HttpResponse("Invalid URL")


def reset_password(request, reset_token):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password!= confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password', reset_token=reset_token)
        if validate_password(new_password):
            messages.error(request, 'Password must be at least 8 characters long')
            messages.error(request, 'Password must contain at least 1 uppercase letter')
            messages.error(request, 'Password must contain at least 1 lowercase letter')
            messages.error(request, 'Password must contain at least 1 number')
            return redirect('reset_password', reset_token=reset_token)

        profile = UserProfile.objects.get(pwd_reset_token=reset_token)
        if not profile:
            return HttpResponse("Invalid URL")

        user = profile.user
        user.set_password(new_password)
        user.save()
        profile.pwd_reset_token = None
        profile.save()
        messages.success(request, 'Password reset successfully')
        return redirect('login')
    
    return render(request, 'account/reset_password.html', {'reset_token': reset_token})



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        profile_object = UserProfile.objects.get(user__email=email)
        if not profile_object:
            messages.error(request, 'Email does not exist')
            return redirect('forgot_password')
        else:
            email_token = profile_object.get_reset_password_token()
            try:
                utils.send_password_reset_email(email, email_token)
            except Exception as e:
                logger.warning(f'Error sending email {e}')
            messages.success(request, 'Email sent successfully')
            return redirect('forgot_password')


    return render(request, 'account/forgot_password.html')



@login_required(redirect_field_name='next',login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user

        if validate_password(new_password):
            messages.error(request, 'Password must be at least 8 characters long')
            messages.error(request, 'Password must contain at least 1 uppercase letter')
            messages.error(request, 'Password must contain at least 1 lowercase letter')
            messages.error(request, 'Password must contain at least 1 number')
            return redirect('change_password')
        
        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
                logger.info(f'Password changed successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Passwords do not match')
                logger.error(f'Passwords do not match')
                return redirect('change_password')
        else:
            messages.error(request, 'Incorrect password')
            logger.error(f'Incorrect password')
            return redirect('change_password')
    return render(request, 'account/change_password.html')

def logout(request):
    user_profile = UserProfile.objects.get(user__email=request.user.email)
    user_profile.is_otp_verified = False
    user_profile.save()
    auth_logout(request)
    return redirect('index')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=email)
        #  print(f'Log in password >>>>>>>>>>: {password}')
        # print(f'User object>>>>> {user_obj}')

        if not user_obj.exists():
            messages.error(request, 'User does not exist')
            return HttpResponseRedirect(request.path_info)
        #authenticate a user
        user_obj = authenticate(username=email, password=password)
        # print(f'Log in user obj >>>>>>>>>>: {user_obj}')
        if user_obj:
            #log in the authenticated user
            # auth_login(request, user_obj)
            otp = randint(100000, 999999)
            user_profile = UserProfile.objects.get(user=user_obj)
            user_profile.otp = otp
            user_profile.save()
            utils.send_login_otp(email, otp)
            request.session['email'] = email
            # user_obj.otp = otp
            return redirect('verify_otp', user_id=user_profile.uid)
        else:
            messages.error(request, 'Invalid credentials')
            logger.error(f'Invalid credentials')
            return HttpResponseRedirect(request.path_info)
        
    return render(request, 'account/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        if validate_password(password):
            messages.error(request, 'Password must be at least 8 characters long')
            messages.error(request, 'Password must contain at least 1 uppercase letter')
            messages.error(request, 'Password must contain at least 1 lowercase letter')
            messages.error(request, 'Password must contain at least 1 number')
            return HttpResponseRedirect(request.path_info)
        
        # print(f'Register password >>>>>>>>: {password}')
        if not first_name or not last_name or not email or not phone_number or not password:
            messages.error(request, 'Please fill all the fields')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = User.objects.filter(email=email)

        if user_obj.exists():
            messages.error(request, 'User already exists')
            return HttpResponseRedirect(request.path_info)

        
        user_obj = User.objects.create(email=email,first_name=first_name, last_name=last_name, username=email)
        user_obj.set_password(password)
        user_obj.save()
        user_profile = UserProfile(user=user_obj, phone=phone_number)
        user_profile.save()

        messages.success(request, 'User registered successfully')
        return HttpResponseRedirect(request.path_info)

        
    return render(request, 'account/register.html')


@login_required(redirect_field_name='next',login_url='login')
def add_to_cart(request, product_uid):
    size = request.GET.get('size')
    quantity = int(request.GET.get('quantity'))
    product = Product.objects.get(uid=product_uid)
    #create cart object if it does not exist
    cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    if size:
        size_variant = SizeVariant.objects.get(size=size)
        cartItem, _ = CartItem.objects.get_or_create(cart=cart, product=product, size_variant=size_variant)
        cartItem.size_variant=size_variant
        cartItem.quantity += quantity  
        cartItem.save()
  
  
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(redirect_field_name='next',login_url='login')
def show_cart(request):
    cart=None
    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
    except Cart.DoesNotExist:
        return redirect('index')
    
    payment = None

    if cart:
        client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY'), os.getenv('RAZORPAY_SECRET')))
        # print(f'razor pay client >>>>>>> {os.getenv('RAZORPAY_KEY')} {os.getenv('RAZORPAY_SECRET')}')
        if cart.get_total_price() > 1:
            payment = client.order.create({'amount': int(cart.get_total_price()) * 100, 'currency': 'INR', 'payment_capture': 1})
            cart.razorpay_payment_id = payment['id']
            cart.save()
            # print(f'payment object: {payment}')

    context = {'cart': cart, 'payment': payment}
    return render(request, 'account/cart.html', context)


@login_required(redirect_field_name='next',login_url='login')
def remove_cart_item(request, cart_item_uid):
    try:
        cart_item = CartItem.objects.get(uid=cart_item_uid)
        cart_item.delete()
        # messages.success(request, 'Item removed from cart')
    except CartItem.DoesNotExist:
        pass

    return redirect(request.META.get('HTTP_REFERER'))

@login_required(redirect_field_name='next',login_url='login')
def payment_success(request):
    order_id = request.GET.get('razorpay_order_id')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    cart = Cart.objects.get(razorpay_payment_id=order_id)
    cart.razorpay_order_id = order_id
    cart.razorpay_payment_id = razorpay_payment_id
    cart.razorpay_payment_signature = razorpay_signature
    cart.is_paid = True
    cart.save()
    return render(request, 'account/payment_success.html')