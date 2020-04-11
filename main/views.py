from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from main import forms as user_forms
from main import models

import logging

logger = logging.getLogger(__name__)

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