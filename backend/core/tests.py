from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from .models import Member

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

class NotificationAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.member = Member.objects.create(username='testuser', notifications=[
            {'text': '你被配對了！', 'timestamp': now().isoformat(), 'read': False},
            {'text': '有人喜歡你！', 'timestamp': now().isoformat(), 'read': True}
        ])

    def test_unread_count(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/unread_notification_count/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
    
    def test_get_notifications_marks_as_read(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['notifications']), 2)
        self.assertTrue(all('time' in n for n in data['notifications']))

        self.member.refresh_from_db()
        for n in self.member.notifications:
            self.assertTrue(n.get('read'))