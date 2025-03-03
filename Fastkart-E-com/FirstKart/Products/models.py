from django.db import models
from django.utils.text import slugify
from accounts.models import CustomUser
from django.db.models import Avg, Count


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="categories")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs): # Save the category slug based on the category name. If no name, return an empty string.
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    unit = models.CharField(max_length=100,  null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs): ## Save the product slug based on the product name. If no name, return an empty string.
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)
        
    
    @property # Calculate the discounted price based on the discount percentage. If no discount, return the original price.
    def discount_price(self):
        return self.price * (1 - self.discount_percentage / 100)
    
    @property
    def savings(self):
        """Calculate the savings by subtracting the discount price from the original price."""
        return self.price - self.discount_price
    def get_discounted_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price
   
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name
# 2nd after review
    def averageReview(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        self.rating = avg
        return avg

    def countReview(self):
        reviews = Review.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
#After cart
    def is_in_cart(self, request):
        """Check if the product is in the cart."""
        from carts.models import CartItem
        from carts.views import _cart_id
        is_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=self).exists()
        print(is_cart)
        return is_cart
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images')

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    rating = models.FloatField()
    review = models.TextField(max_length=500, blank=True)
    
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'