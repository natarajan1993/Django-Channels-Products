from django import forms
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField

from .models import User

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