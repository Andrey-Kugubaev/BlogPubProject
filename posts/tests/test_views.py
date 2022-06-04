from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Группа теста',
            slug='group_test',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост тестовый',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_pages_template(self):
        post = PostPagesTests.post
        templates_pages_names = {
            'posts/index.html': reverse('posts:posts_list'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': 'group_test'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': 'testuser'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': post.id}),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_pages_auth_template(self):
        post = PostPagesTests.post
        templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': post.id}): 'posts/create_post.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_context(self):
        response = self.guest_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Пост тестовый')
        self.assertEqual(post_group_0, 'Группа теста')

    def test_group_list_context(self):
        response = self.guest_client.get(reverse('posts:group_list', kwargs={'slug': 'group_test'}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_title_0 = first_object.group.title
        post_group_slug_0 = first_object.group.slug
        post_group_description_0 = first_object.group.description
        self.assertEqual(post_text_0, 'Пост тестовый')
        self.assertEqual(post_group_title_0, 'Группа теста')
        self.assertEqual(post_group_slug_0, 'group_test')
        self.assertEqual(post_group_description_0, 'Описание группы')

    def test_profile_context(self):
        post = PostPagesTests.post
        author = PostPagesTests.post.author
        response = self.guest_client.get(reverse('posts:profile', kwargs={'username': post.author}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, 'Пост тестовый')
        self.assertEqual(post_author_0, author)

    def test_post_context(self):
        post = PostPagesTests.post
        response = (self.guest_client.get(reverse('posts:post_detail', kwargs={'post_id': post.pk})))
        self.assertEqual(response.context.get('post').text, 'Пост тестовый')
        self.assertEqual(response.context.get('post').group.title, 'Группа теста')

    #def test_post_edit_context(self):
    #    post = PostPagesTests.post
    #    response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': post.pk}))
    #    form_fields = {
    #        'is_edit': forms.fields.CharField,
    #        'groups': forms.fields.ChoiceField,
    #        'post': forms.fields.CharField,
    #    }
    #    for value, expected in form_fields.items():
    #        with self.subTest(value=value):
    #            form_field = response.context.get('form').fields.get(value)
    #            self.assertIsInstance(form_field, expected)

    #def test_post_create_context(self):
    #    post = PostPagesTests.post
    #    response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': post.id}))
    #    form_fields = {
    #        'form': forms.fields.CharField,
    #        'groups': forms.fields.CharField,
    #    }
    #    for value, expected in form_fields.items():
    #        with self.subTest(value=value):
    #            form_field = response.context.get('form').fields.get(value)
    #            self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user test')
        cls.group = Group.objects.create(
            title='Группа группа',
            slug='test_groups',
            description='Описание группы',
        )
        for count in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {count}',
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = PaginatorViewsTest.user

    def test_first_pages(self):
        post = PaginatorViewsTest.post
        pages_count = {
            reverse('posts:posts_list'): 10,
            reverse('posts:group_list', kwargs={'slug': 'test_groups'}): 5,
            reverse('posts:profile', kwargs={'username': post.author}): 10,
        }

        for reverse_page, count in pages_count.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page)
                self.assertEqual(len(response.context['page_obj']), count)

    def test_second_pages(self):
        post = PaginatorViewsTest.post
        pages_count = {
            reverse('posts:posts_list') + '?page=2': 5,
            reverse('posts:group_list', kwargs={'slug': 'test_groups'}) + '?page=2': 5,
            reverse('posts:profile', kwargs={'username': post.author}) + '?page=2': 5,
        }

        for reverse_page, count in pages_count.items():
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page)
                self.assertEqual(len(response.context['page_obj']), count)


# class PostViewsTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.user = User.objects.create_user(username='user_user')
#         cls.group = Group.objects.create(
#             title='Группа_группа',
#             slug='test_group',
#             description='Описание группы',
#         )
#         cls.post = Post.objects.create(
#             author=cls.user,
#             text='В лесу родилась елочка',
#             group=cls.group
#         )
#
#     def setUp(self):
#         self.guest_client = Client()
#         self.user = PostViewsTest.user
#
#     def test_post_view_index(self):

