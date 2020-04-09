from django.test import TestCase

class TestPage(TestCase):
    def test_home_page_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')
        self.assertContains(response, 'BookTime')