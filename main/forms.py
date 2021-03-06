from django import forms
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory

from .models import User, Basket, BasketLine, Address
from .widgets import PlusMinusNumberInput

import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(f"Sending signup email to {self.cleaned_data['email']}")

        message = f"Welcome to Booktime {self.cleaned_data['email']}"

        send_mail("Welcome to Booktime",
                    message,
                    "admin@booktime.com",
                    [self.cleaned_data['email']],
                    fail_silently=True)

class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip = False, widget = forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request, email = email, password = password)

            if self.user is None:
                raise forms.ValidationError("Please check your email and password again")

            logger.info(f"Successfully authenticated email {email}")
    
        return self.cleaned_data
    
    def get_user(self):
        return self.user


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length = 100)
    message = forms.CharField(label='Message', max_length = 600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Sending email to customer service")

        message = f"From: {self.cleaned_data['name']}\n{self.cleaned_data['message']}"

        send_mail("Site message", # Subject
                    message, # Message
                    "site@booktime.com", # From
                    ["natrajm93@gmail.com"], # To
                    fail_silently=False)


"""Formsets can quickly bulk create related forms. we use inline because the models are related.
    This will create a form for all Basketline objects connected to the basket with the only
    editable field being the quantity. Formsets can also do CRUD operations"""
BasketLineFormset = inlineformset_factory(
    Basket,
    BasketLine,
    fields = ("quantity",),
    extra = 0,
    widgets = {"quantity": PlusMinusNumberInput()},
)


class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset = None)
    shipping_address = forms.ModelChoiceField(queryset = None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset
