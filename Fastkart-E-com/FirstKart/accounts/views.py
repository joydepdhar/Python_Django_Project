from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser, UserProfile

User = get_user_model()

### 🏠 **User Dashboard**
@login_required
def user_dashboard(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        user_profile.mobile = request.POST.get('mobile', user_profile.mobile)
        user_profile.address_line_1 = request.POST.get('address_line_1', user_profile.address_line_1)
        user_profile.address_line_2 = request.POST.get('address_line_2', user_profile.address_line_2)
        user_profile.city = request.POST.get('city', user_profile.city)
        user_profile.state = request.POST.get('state', user_profile.state)
        user_profile.country = request.POST.get('country', user_profile.country)
        user_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_dashboard')

    return render(request, 'accounts/user_dashboard.html', {'user_info': user})

### 🔐 **Signup**
def signup(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not full_name or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with that email already exists.")
            return redirect('signup')

        try:
            user = CustomUser.objects.create_user(username=full_name, email=email, password=password)
            user.is_verified = False
            user.save()

            messages.success(request, "Registration successful. Please verify your email.")
            
            current_site = get_current_site(request)
            verification_link = f"http://{current_site.domain}/accounts/verify/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}"
            
            send_verification_email(user, verification_link)
            return redirect('login')
        except Exception as e:
            messages.error(request, "An error occurred while creating the account.")
            return redirect('signup')

    return render(request, 'accounts/sign-up.html')

### 📩 **Send Verification Email**
def send_verification_email(user, verification_link):
    email_subject = 'Verify Your Email Address'
    email_body = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_link': verification_link
    })
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
    email.content_subtype = 'html'
    email.send()

### ✅ **Verify Email**
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, 'Your email has been verified successfully.')
        return redirect('login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('signup')

### 🔑 **User Login**
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Retrieve the user by email
        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

        # Authenticate using the user's username
        user = authenticate(request, username=user_obj.username, password=password)

        if user and user.is_verified:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/login.html')

### 🚪 **User Logout**
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

### 🔄 **Password Reset**
def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            reset_link = f"http://{current_site.domain}/accounts/password_reset_confirm/{urlsafe_base64_encode(force_bytes(user.pk))}/{default_token_generator.make_token(user)}"
            send_password_reset_email(user, reset_link)
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('login')
        else:
            messages.error(request, "User does not exist.")

    return render(request, 'accounts/forgot.html')

### 📩 **Send Password Reset Email**
def send_password_reset_email(user, reset_link):
    email_subject = 'Reset Your Password'
    email_body = render_to_string('accounts/password_reset_email.html', {
        'user': user,
        'reset_link': reset_link
    })
    email = EmailMessage(subject=email_subject, body=email_body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
    email.content_subtype = 'html'
    email.send()

### 🔑 **Password Reset Confirm**
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['reset_user_id'] = user.pk  # Store user ID in session
        return redirect('newpassword')
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect('signup')

### 🔑 **New Password View (Fix for AnonymousUser Issue)**
def newpassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user_id = request.session.get('reset_user_id')  # Retrieve user ID from session

        if not user_id:
            messages.error(request, "Session expired or invalid request.")
            return redirect('login')

        user = get_object_or_404(CustomUser, pk=user_id)
        user.set_password(password)
        user.save()

        messages.success(request, "Password updated successfully. Please log in.")
        return redirect('login')

    return render(request, 'accounts/newpassword.html')

### 👤 **Update Profile**
@login_required
def update_profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()

        user_profile.mobile = request.POST.get('mobile', user_profile.mobile)
        user_profile.address_line_1 = request.POST.get('address_line_1', user_profile.address_line_1)
        user_profile.address_line_2 = request.POST.get('address_line_2', user_profile.address_line_2)
        user_profile.city = request.POST.get('city', user_profile.city)
        user_profile.state = request.POST.get('state', user_profile.state)
        user_profile.country = request.POST.get('country', user_profile.country)
        user_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user_dashboard')

    return render(request, 'accounts/user_dashboard.html', {'user_info': user})
