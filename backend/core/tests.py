from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)  # 通常登入成功會 redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)