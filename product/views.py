from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import Product

@login_required(redirect_field_name='next',login_url='login')
def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        selected_size = request.GET.get('size')
        context = {'product': product}

        if selected_size:
            updated_price = product.get_updated_price_by_size(selected_size)
            context['selected_size'] = selected_size
            context['updated_price'] = updated_price
        
        return render(request, 'product/product.html', context)
    except Product.DoesNotExist:
        return render(request, '404.html')