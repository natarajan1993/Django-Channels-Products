from django.test import TestCase
from django.urls import reverse

from main import forms as user_forms

class TestPage(TestCase):
    def test_home_page_route(self):
        response = self.client.get(reverse('app-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        self.assertContains(response, 'BookTime')

    def test_about_page_route(self):
        response = self.client.get(reverse('app-about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/about.html')
        self.assertContains(response, 'About us')
    
    def test_contact_page_route(self):
        response = self.client.get(reverse('contact-us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/contact_form.html')
        self.assertContains(response, 'BookTime')
        self.assertIsInstance(response.context['form'],user_forms.ContactForm)