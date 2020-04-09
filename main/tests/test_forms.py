from django.test import TestCase
from django.core import mail

from main import forms as user_forms

class TestForm(TestCase):
    def test_valid_contact_form_sends_email(self):
        test_form = user_forms.ContactForm({
            "name":"Nate",
            "message":"Testing contact forms email"
        })

        self.assertTrue(test_form.is_valid())
        with self.assertLogs('main.forms', level='INFO') as cm:
            test_form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Site message")

        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_form(self):
        test_form = user_forms.ContactForm({
            "name":"Nate"
        })

        self.assertFalse(test_form.is_valid())
        
