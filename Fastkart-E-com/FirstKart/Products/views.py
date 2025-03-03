from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Product, Category, Review
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.
def home(request):
    products = Product.objects.all()
    categories = Category.objects.annotate(product_count=Count('products'))
    
    context={
            'products': products,
            'categories': categories
        }
    
    return render(request, 'products/home.html', context)

def category_products(request, category_slug):
    # Get the category based on the slug
    category = get_object_or_404(Category, slug=category_slug)
    
    products = Product.objects.filter(category=category)# Filter products by the selected category
    # Paginate the products
    paginator = Paginator(products, 6) 
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    #paginate end
    context = {
        'products': paged_products, 
        'category': category,
        }
    return render(request, 'products/category_products.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    reviews = product.reviews.filter(status=True)
    
    # Count the occurrences of each rating (1 to 5)
    #rating__gt (greater than) and rating__lte (less than or equal to)
    rating_counts = {
        '5': product.reviews.filter(rating__gt=4.4, rating__lte=5.1).count(),
        '4': product.reviews.filter(rating__gt=3.4, rating__lte=4.1).count(),
        '3': product.reviews.filter(rating__gt=2.4, rating__lte=3.1).count(),
        '2': product.reviews.filter(rating__gt=1.4, rating__lte=2.1).count(),
        '1': product.reviews.filter(rating__gt=0.4, rating__lte=1.1).count(),
    }


    # Calculate the total number of reviews
    total_reviews = sum(rating_counts.values())

    # Calculate the percentage for each rating
    rating_percentages = {
        '5': (rating_counts['5'] / total_reviews * 100) if total_reviews else 0,
        '4': (rating_counts['4'] / total_reviews * 100) if total_reviews else 0,
        '3': (rating_counts['3'] / total_reviews * 100) if total_reviews else 0,
        '2': (rating_counts['2'] / total_reviews * 100) if total_reviews else 0,
        '1': (rating_counts['1'] / total_reviews * 100) if total_reviews else 0,
    }

    context = {
        'product': product,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
        'reviews': reviews,
    }
    return render(request, 'products/product-left-thumbnail.html', context)

@login_required
def submit_review(request, product_slug):
    url = request.META.get('HTTP_REFERER') # for geting current html page
    if request.method == 'POST':
        try:
            reviews = Review.objects.get(user__id=request.user.id, product__slug=product_slug)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except Review.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Review()
                data.product = Product.objects.get(slug=product_slug)
                data.user_id = request.user.id
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)