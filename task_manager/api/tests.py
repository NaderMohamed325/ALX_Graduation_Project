from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Task
from django.utils import timezone
import datetime


class AuthTests(APITestCase):
    def test_register_and_login(self):
        r = self.client.post(reverse('register'), {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'StrongPass123'
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', r.data)

        r2 = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'StrongPass123'
        }, format='json')
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn('user', r2.data)
        
    def test_logout(self):
        """Test logout endpoint"""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        token, _ = Token.objects.get_or_create(user=user)
        self.client.cookies['auth_token'] = token.key
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check token was deleted from database
        self.assertEqual(Token.objects.filter(user=user).count(), 0)
        
    def test_login_with_email(self):
        """Test login with email"""
        User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('auth_token' in response.cookies)
        
    def test_reject_invalid_credentials(self):
        """Test invalid login credentials"""
        User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='bob', email='bob@example.com', password='Pass12345')
		login = self.client.post(reverse('login'), {'username': 'bob', 'password': 'Pass12345'}, format='json')
		# Extract token cookie
		self.token = self.client.cookies.get('auth_token').value if 'auth_token' in self.client.cookies else None
		self.auth_client = APIClient()
		if self.token:
			self.auth_client.cookies['auth_token'] = self.token

	def test_task_lifecycle(self):
		# Create
		create_resp = self.auth_client.post(reverse('task_list_create'), {
			'title': 'Test Task',
			'description': 'Desc'
		}, format='json')
		self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
		task_id = create_resp.data['id']

		# List
		list_resp = self.auth_client.get(reverse('task_list_create'))
		self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
		self.assertEqual(len(list_resp.data), 1)

		# Detail
		det_resp = self.auth_client.get(reverse('task_detail', args=[task_id]))
		self.assertEqual(det_resp.status_code, status.HTTP_200_OK)
		self.assertEqual(det_resp.data['title'], 'Test Task')

		# Update
		upd_resp = self.auth_client.put(reverse('task_detail', args=[task_id]), {
			'title': 'Updated',
			'description': 'New'
		}, format='json')
		self.assertEqual(upd_resp.status_code, status.HTTP_200_OK)
		self.assertEqual(upd_resp.data['title'], 'Updated')

		# Complete
		comp_resp = self.auth_client.patch(reverse('task_complete', args=[task_id]))
		self.assertEqual(comp_resp.status_code, status.HTTP_200_OK)
		self.assertTrue(comp_resp.data['completed'])

		# Incomplete
		inc_resp = self.auth_client.patch(reverse('task_incomplete', args=[task_id]))
		self.assertEqual(inc_resp.status_code, status.HTTP_200_OK)
		self.assertFalse(inc_resp.data['completed'])

		# Delete
		del_resp = self.auth_client.delete(reverse('task_detail', args=[task_id]))
		self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Task.objects.filter(id=task_id).exists())
