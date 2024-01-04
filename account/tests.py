from django.test import TestCase

# Create your tests here.
import unittest
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from account.models import UserProfile, Cart, CartItem, Category, SizeVariant
from account.views import add_to_cart, remove_cart_item
from product.models import Product 

class CartTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='secret')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name="XL")
        self.size_variant = SizeVariant.objects.create(size='XL')
    
    def test_add_to_cart_url(self):
        # Create a sample product
        product = Product.objects.create(name='Test Product 1', price=100, category=self.category)

        # Generate URL
        url = reverse('add_to_cart', args=[product.uid])
        
        # Verify URL resolves to add_to_cart view
        self.assertEqual(resolve(url).func, add_to_cart)

    def test_add_to_cart(self):
        # Create a sample product
        product = Product.objects.create(name='Test Product 2', price=100, category=self.category)
        
        # Call add_to_cart view
        self.client.force_login(self.user)
        response = self.client.get(reverse('add_to_cart', args=[product.uid]), {'size': 'XL', 'quantity': 1})
        cart_items = CartItem.objects.all()
        # Verify cart item was added
        cart_item = CartItem.objects.get(cart=self.cart, product=product)
        
        self.assertEqual(cart_item.quantity, 1)

    def test_remove_cart_item_url(self):
         # Create a sample cart item
        cart_item = CartItem.objects.create(cart=self.cart, quantity=1)

        # Generate URL
        url = reverse('remove_cart_item', args=[cart_item.uid])
        
        # Verify URL resolves to remove_cart_item view
        self.assertEqual(resolve(url).func, remove_cart_item)

    # ... other tests
    
if __name__ == '__main__':
    unittest.main()