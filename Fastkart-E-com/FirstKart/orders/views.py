# from django.shortcuts import render, redirect
# from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
# from carts.models import CartItem
# from orders.models import Order, Payment, OrderProduct
# from Products.models import Product
# import datetime
# from .models import Order, Payment, OrderProduct
# import json
# from Products.models import Product
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# from accounts.models import UserProfile
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse
# from django.conf import settings
# from accounts.models import UserProfile

# #for sslcommerce
# from decimal import Decimal
# # from sslcommerz_python_api import SSLCSession

# import os
# # from dotenv import load_dotenv



# # Load environment variables from .env file
# # load_dotenv()

# # Get SSLCOMMERZ credentials from .env
# SSLCOMMERZ_STORE_ID = os.getenv("sslc_store_id")
# SSLCOMMERZ_STORE_PASS = os.getenv("sslc_store_pass")


# # Create your views here.
# @csrf_exempt
# @login_required
# def place_order(request, total=0, quantity=0,):
#     current_user = request.user
    
#         # Retrieve user profile data
#     try:
#         user_profile = UserProfile.objects.get(user=current_user)
#     except UserProfile.DoesNotExist:
#         return HttpResponse("User profile does not exist.")

#     # If the cart count is less than or equal to 0, then redirect back to shop
#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('home')
    
#     grand_total = 0
#     total = 0
#     for cart_item in cart_items:
#         total += (cart_item.product.price * cart_item.quantity)
#         quantity += cart_item.quantity
#     grand_total = float(total) + float(6.90)
    
    
#     if request.method == 'POST':
#         payment_option = request.POST.get('flexRadioDefault', 'cash')
        
#         try:
#             # Generate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             d = datetime.date(yr,mt,dt)
#             current_date = d.strftime("%Y%m%d") #20250221
#             order_number = current_date + str(cart_count) #20250221001
            
            
#             order = Order.objects.create(
#                 user=current_user,
#                 mobile=user_profile.mobile,
#                 email=current_user.email,
#                 address_line_1=user_profile.address_line_1,
#                 address_line_2=user_profile.address_line_2,
#                 country=user_profile.country,
#                 state=user_profile.state,
#                 city=user_profile.city,
#                 order_note=request.POST.get('order_note', ''),
#                 order_total=grand_total,
#                 status='New',
#                 order_number=order_number,
#             )
#             for cart_item in cart_items:
#                 order_product = OrderProduct.objects.create(
#                     order=order,
#                     product=cart_item.product,
#                     quantity=cart_item.quantity,
#                     product_price=cart_item.product.price,
#                     user=user_profile, 
#                 )
#                 # Update product stock after order placement
#                 product = Product.objects.get(id=cart_item.product.id)
#                 if product.stock >= cart_item.quantity:
#                     product.stock -= cart_item.quantity
#                     product.save()
#                 else:
#                     # Handle the case where there is not enough stock
#                     return HttpResponse("Not enough stock available for product: {}".format(product.name))
                
#                 cart_item.delete()
#             #send order confirmation email
            
#             send_order_confirmation_email(current_user, order)
            
#             if payment_option == 'cash':
#                 return redirect('order_complete')
#             elif payment_option == 'sslcommerz':
#                 return redirect("payment")
            
#         except Exception as e:
#             return HttpResponse('Error occurred: ' + str(e))
    
#     context = {
#         'user':current_user,
#         'cart_items': cart_items,
#         'grand_total': grand_total,
#         'total': total,
#     }
#     return render(request, 'orders/checkout.html', context)

# def payment(request):
    
#     mypayment = SSLCSession(
#     sslc_is_sandbox=True,
#     sslc_store_id=os.getenv("sslc_store_id"),
#     sslc_store_pass=os.getenv("sslc_store_pass")
#     )
    
#     status_url = request.build_absolute_uri('sslc/status')

#     mypayment.set_urls(
#     success_url=status_url,
#     fail_url=status_url,
#     cancel_url=status_url,
#     ipn_url=status_url
#     )
    
#     order = Order.objects.filter(user=request.user, is_ordered=False).last()

#     mypayment.set_product_integration(
#     total_amount=Decimal(order.order_total),
#     currency='BDT',
#     product_category='clothing',
#     product_name='demo-product',
#     num_of_item=2,
#     shipping_method='YES',
#     product_profile='None'
#     )

#     mypayment.set_customer_info(
#     name=order.user.username,
#     email=order.user.email,
#     address1=order.address_line_1,
#     address2=order.address_line_1,
#     city=order.city, 
#     postcode='1207',
#     country=order.country,
#     phone=order.mobile
#     )

#     mypayment.set_shipping_info(
#     shipping_to='demo customer',
#     address='demo address',
#     city='Dhaka',
#     postcode='1209',
#     country='Bangladesh'
#     )



#     response_data = mypayment.init_payment()

#     # You can Print the response data
#     print(response_data)
    
    
#     return redirect(response_data['GatewayPageURL'])

# @csrf_exempt 
# def payment_status(request):
#     if request.method  == 'POST' or request.method  == 'post':
#         payment_data = request.POST
        
#         if payment_data['status'] == 'VALID':
            
            
#             val_id = payment_data['val_id']
#             tran_id = payment_data['tran_id']

            
#             return HttpResponseRedirect(reverse('sslc_complete', kwargs= {'val_id': val_id, 'tran_id': tran_id}))
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Payment failed'})
    
    
#     return render(request, 'orders/status.html')
    
# def sslc_complete(request, val_id, tran_id):
#        # Get the order that needs to be completed
#     try:
#         # Get the UserProfile instance for the current user
#         user_profile = UserProfile.objects.get(user=request.user)
        
#         # Get the order that needs to be completed
#         order = Order.objects.filter(user=request.user, is_ordered=False).last()
        
#         # Update order status
#         order.is_ordered = True
#         order.status = 'Completed'
        
#         # Create payment record with UserProfile
#         payment = Payment(
#             user=user_profile,  # Use user_profile instead of request.user
#             payment_id=val_id,
#             payment_method='SSLCommerz',
#             amount_paid=order.order_total,
#             status='Completed'
#         )
#         payment.save()
        
#         # Update the order with payment information
#         order.payment = payment
#         order.save()
        
#         # Clear the user's cart
#         cart_items = CartItem.objects.filter(user=request.user)
#         cart_items.delete()
        
#         context = {
#             'order': order,
#             'transaction_id': tran_id,
#         }
#         return render(request, 'orders/status.html', context)
        
#     except Order.DoesNotExist:
#         return HttpResponse("Order not found", status=404)
#     except Exception as e:
#         return HttpResponse(f"An error occurred: {str(e)}", status=500)

# def  send_order_confirmation_email(user, order):
#     # Retrieve user profile data
#     try:
#         user_profile = UserProfile.objects.get(user=user)
#     except UserProfile.DoesNotExist:
#         return HttpResponse("User profile does not exist.")
    
#     # Render the email template with context
#     email_subject = 'Thanks For your Order'
#     email_body = render_to_string('orders/order-success.html', {
#         'user':  user_profile,
#     })

#     # Create the email message
#     email = EmailMessage(
#         subject=email_subject,
#         body=email_body,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user.email],
#     )

#     # Send the email
#     email.content_subtype = 'html'  # Ensure the email is sent as HTML
#     email.send()