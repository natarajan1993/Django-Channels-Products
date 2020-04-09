from django.shortcuts import render
from django.views.generic import FormView

from main import forms as user_forms

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