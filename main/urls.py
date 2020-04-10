from django.urls import path
from django.views.generic.detail import DetailView

from .views import home, about, ContactFormView, ProductListView
from main import models

urlpatterns = [
    path('',home, name = 'app-home'),
    path('about/', about, name='app-about'),
    path('contact_us/', ContactFormView.as_view(), name='contact-us'),

    path('products/<slug:tag>/', ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(model=models.Product), name='product'),


]
