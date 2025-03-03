from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('category_products/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:product_slug>/review/', views.submit_review, name='submit_review'),

]