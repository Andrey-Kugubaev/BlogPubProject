from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse

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


# class UserFormTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#
#     def setUp(self):
#         self.guest_client = Client()
#
#     def test_new_user(self):
#         users_count = User.objects.count()
#         form_data = {
#             'first_name': 'Добрыня',
#             'last_name': 'Никитыч',
#             'username': 'bogatir2',
#             'email': 'ukamnya@triputi.ru'
#         }
#         response = self.guest_client.post(reverse('users:signup'), data=form_data)
#         #self.assertEqual(User.objects.count(), users_count + 1)
