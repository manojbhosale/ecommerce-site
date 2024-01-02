from django.db import models
from base.models import BaseModel
from django.utils.text import slugify

# Create your models here.




class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to='category_images', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.name} - {self.slug}'
    

class SizeVariant(BaseModel):
    size = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.size
    
class Product(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    size_variants = models.ManyToManyField(SizeVariant, related_name='products', blank=True)

    def get_updated_price_by_size(self, size):
        size_obj = SizeVariant.objects.get(size=size)
        return self.price + size_obj.price

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.name} - {self.slug}'