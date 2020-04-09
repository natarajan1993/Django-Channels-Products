from django.urls import path

from .views import home, about, ContactFormView

urlpatterns = [
    path('',home, name = 'app-home'),
    path('about/', about, name='app-about'),
    path('contact_us/', ContactFormView.as_view(), name='contact-us')
]
