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
    def test_input_login_required_view(self):
        protected_url = reverse('input')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 302)  # 未登入時會 redirect 到登入頁
        self.assertIn('/login/', response.url)
        # 登入後再訪問
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 200)
    def test_status_login_required_view(self):
        protected_url = reverse('status')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 302)  # 未登入時會 redirect 到登入頁
        self.assertIn('/login/', response.url)
        # 登入後再訪問
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, 200)
    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # 通常登出也會 redirect
        response = self.client.get('/')  # 再訪問一個頁面來檢查是否已登出
        self.assertFalse(response.wsgi_request.user.is_authenticated)