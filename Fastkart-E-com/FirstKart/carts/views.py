from django.shortcuts import render, redirect, get_object_or_404
from Products.models import Product
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key # Get the cart ID from the session
    if not cart:
        cart = request.session.create() # Create a new session key if it doesn't exist
    return cart

def add_cart(request, product_slug):
    url = request.META.get('HTTP_REFERER') # for geting current html page
    product = Product.objects.get(slug=product_slug)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart object associated with the current session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request)) # Create a new cart if it doesn't exist
    cart.save()
    
    # Check if the product is already in the cart
    # if the product is already in the cart, increment its quantity
    # else, add the product to the cart with a quantity of 1
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart) # Check if the product is already in the cart
        cart_item.quantity += 1 # Increment the quantity of the product in the cart
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product, 
            cart=cart,
            user=request.user, 
            quantity=1) # Add the product to the cart if it's not already there
        cart_item.save()
    return redirect(url) # Redirect to the cart page after adding the product to the cart
        
     
def remove_cart(request, product_slug):
    url = request.META.get('HTTP_REFERER')

    product = get_object_or_404(Product, slug=product_slug)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect(url)        
 
def remove_cart_item(request, product_slug):
    url = request.META.get('HTTP_REFERER')
    product = get_object_or_404(Product, slug=product_slug)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect(url)

        
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0
        total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.discount_price * cart_item.quantity)
            quantity += cart_item.quantity
        grand_total = float(total) + float(6.90)
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total'     : total,
        'quantity'  : quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'carts/cart.html', context)