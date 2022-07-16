from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_url(self):
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_template(self):
        response = self.guest_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')
