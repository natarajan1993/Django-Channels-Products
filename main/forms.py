from django import forms
from django.core.mail import send_mail

import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

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