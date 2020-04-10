from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView
from django.views.generic.list import ListView

from main import forms as user_forms
from main import models

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

