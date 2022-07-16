from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testik')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_guest_urls(self):
        post = PostURLTests.post
        list_url_names = ['/', '/group/test_group/', '/profile/testik/', f'/posts/{post.pk}/']
        for address in list_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_all_auth_urls(self):
        post = PostURLTests.post
        list_auth_url_names = [f'/posts/{post.pk}/edit/', '/create/']
        for address in list_auth_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url(self):
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_unknown_url(self):
        response = self.guest_client.get('/unknown/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_all_templates(self):
        post = PostURLTests.post
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_group/',
            'posts/profile.html': '/profile/testik/',
            'posts/post_detail.html': f'/posts/{post.pk}/',
        }
        cache.clear()
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_all_auth_templates(self):
        post = PostURLTests.post
        templates_auth_url_names = {
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_auth_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

class CommentURLtest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='comtestik')
        cls.group = Group.objects.create(
            title='Тестовая группа для комментов',
            slug='test_group_com',
            description='Тестовое описание группы для комментов',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для комментов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = CommentURLtest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_create_url(self):
        post = CommentURLtest.post
        response = self.guest_client.get(f'/posts/{post.pk}/comment/')
        self.assertRedirects(response, f'/auth/login/?next=/posts/{post.pk}/comment/')

    def test_comment_url(self):
        post = CommentURLtest.post
        response = self.guest_client.get(f'/posts/{post.pk}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_auth_comment_url(self):
        post = CommentURLtest.post
        response = self.authorized_client.get(f'/posts/{post.pk}/comment/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
