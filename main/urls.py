from django.urls import path
from django.views.generic.detail import DetailView
from django.contrib.auth import views as auth_views

from .views import (home,
                    about,
                    ContactFormView,
                    ProductListView,
                    SignupView,
                    AddressCreateView,
                    AddressDeleteView,
                    AddressListView,
                    AddressUpdateView)
from .models import Product
from .forms import AuthenticationForm

urlpatterns = [
    path('',home, name = 'app-home'),
    path('about/', about, name='app-about'),
    path('contact_us/', ContactFormView.as_view(), name='contact-us'),

    path('products/<slug:tag>/', ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', DetailView.as_view(model=Product), name='product'),

    path('signup/', SignupView.as_view(), name='sign-up'),
    path('login/', auth_views.LoginView.as_view(template_name="main/login.html",form_class=AuthenticationForm), name="login"),
    
    #We don't specify the template name since Django looks for templates in path <app_name>/<model_name>_<operation>.html
    path('address/', AddressListView.as_view(), name='address_list'),
    path('address/create', AddressCreateView.as_view(), name='address_create'),
    path('address/<int:pk>', AddressUpdateView.as_view(), name='address_update'),
    path('address/<int:pk>/delete', AddressDeleteView.as_view(), name='address_delete'),

]
