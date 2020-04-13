from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django import forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView

from main import forms as user_forms
from main import models

import logging

logger = logging.getLogger(__name__)

class DateInput(forms.DateInput):
    input_type = 'date'

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'user__email':['icontains'],
            'status':['exact'],
            'date_updated': ['gt','lt'],
            'date_added': ['gt','lt'],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter,
                'extra': lambda f: {
                    'widget': DateInput
                }
            }
        }

class OrderView(UserPassesTestMixin, FilterView):
    """OrderView is a view that is only available to users that have access to
        the admin interface as well, as the test_func function checks for that."""
    filterset_class = OrderFilter
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_staff is True

def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

class ContactFormView(FormView):
    template_name = 'main/contact_form.html'
    form_class = user_forms.ContactForm
    success_url = '/'

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)

class SignupView(FormView):
    template_name = 'main/signup.html'
    form_class = user_forms.UserCreationForm
    
    def get_success_url(self):
        return self.request.GET.get("next","/") # Redirect to home

    def form_valid(self, form):
        response =  super().form_valid(form)
        form.save()

        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')

        logger.info(f"New signup for {email} using SignUpView")

        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()

        messages.info(self.request, "You have signed up successfully!")

        return response

class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs['tag'] # This comes from the URL <slug:tag>. We would use a self.request.GET if we put it as a filter parameter or as a form
        self.tag = None
        
        if tag != 'all':
            self.tag = get_object_or_404(models.ProductTag,slug=tag)

        if self.tag:
            products = models.Product.objects.active().filter(tags = self.tag)
        else:
            products = models.Product.objects.active()
        
        return products.order_by("name")



class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = ["name", "address1", "address2", "zip_code", "city", "country"]
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = ["name", "address1", "address2", "zip_code", "city", "country"]
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = 'main/address_select.html'
    form_class = user_forms.AddressSelectionForm
    success_url = reverse_lazy('checkout_done')

    def get_form_kwargs(self):
        """Add the session user to the metadata of the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Once the order is submitted, delete the basket and create the order"""
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(form.cleaned_data['shipping_address'],
                            form.cleaned_data['billing_address'])
        return super().form_valid(form)

def add_to_basket(request):
    """Create the basket and basketline with the products and redirect to the product page after adding
        If the basket does not exist create it
        Add the basket id to the session"""
    product = get_object_or_404(models.Product, pk=request.GET.get("product_id"))
    basket = request.basket

    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
    
        basket = models.Basket.objects.create(user=user)
        request.session['basket_id'] = basket.id

    basketline, created = models.BasketLine.objects.get_or_create(basket=basket, product=product)

    if not created:
        basketline.quantity += 1
        basketline.save()
    
    return HttpResponseRedirect(reverse("product", args = (product.slug,)))


def manage_basket(request):
    """View to render the formset to add products to basket. Returns None to the view if there is no products"""
    if not request.basket:
        return render(request, "main/basket.html", {"formset":None})
    
    if request.method == "POST":
        formset = user_forms.BasketLineFormset(
            request.POST, instance = request.basket
        )

        if formset.is_valid():
            formset.save()
    else:
        formset = user_forms.BasketLineFormset(
            instance = request.basket
        )
    
    if request.basket.is_empty():
        return render(request, "main/basket.html", {"formset":None})
    
    return render(request, "main/basket.html", {"formset":formset})

