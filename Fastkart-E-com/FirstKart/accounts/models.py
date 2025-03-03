from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model extending Django's AbstractUser
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)  # Fixed typo: "is_varified" → "is_verified"

    def __str__(self):
        return self.username

# User Profile model with a OneToOne relationship with CustomUser
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address_1 = models.CharField(null=True, blank=True, max_length=100)
    address_2 = models.CharField(null=True, blank=True, max_length=100)
    profile_picture = models.ImageField(
        null=True, blank=True, upload_to="userprofile"
    )
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    mobile = models.CharField(null=True, blank=True, max_length=50)  # Fixed "black=True" typo

    def __str__(self):
        return self.user.username

    def full_address(self):
        return f'{self.address_1}, {self.address_2}'  # Added comma for readability
