# expenses/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
      
    # check if register page loads
    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expenses/register.html")

    # check if login page loads
    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expenses/login.html")

    # full flow test: register → then login
    def test_user_can_register_and_login(self):
        # Register
        response = self.client.post(self.register_url, {
            "username": "john",
            "password1": "ComplexPass123",
            "password2": "ComplexPass123",
        })
        self.assertIn(response.status_code, (200, 302))

        # Login
        login_response = self.client.post(self.login_url, {
            "username": "john",
            "password": "ComplexPass123",
        })
        self.assertIn(login_response.status_code, (200, 302))
