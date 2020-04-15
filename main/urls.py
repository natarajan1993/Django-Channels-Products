from django.urls import path, include
from django.views.generic.detail import DetailView
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView

from rest_framework import routers

from .views import (home,
                    about,

                    add_to_basket,
                    manage_basket,
                    
                    ContactFormView,
                    SignupView,
                    
                    ProductListView,
                    
                    AddressCreateView,
                    AddressDeleteView,
                    AddressListView,
                    AddressUpdateView,
                    AddressSelectionView,
                    
                    OrderView)
from .models import Product
from .forms import AuthenticationForm
from .endpoints import PaidOrderLineViewSet, PaidOrderViewSet
from main import admin


router = routers.DefaultRouter()
router.register(r'orderlines', PaidOrderLineViewSet)
router.register(r'orders', PaidOrderViewSet)

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

    path("add_to_basket/", add_to_basket, name='add_to_basket'),
    path("basket/", manage_basket, name="basket"),

    path("order/done/", TemplateView.as_view(template_name="main/order_done.html"), name="checkout_done"),
    path("order/address_select/", AddressSelectionView.as_view(), name="address_select"),
    path("order-dashboard/", OrderView.as_view(), name="order-dashboard"),

    path('api/', include(router.urls)),

    path('admin/', admin.main_admin.urls),
    path('office-admin/', admin.central_office_admin.urls),
    path('dispatch-admin/', admin.dispatchers_admin.urls),

]
