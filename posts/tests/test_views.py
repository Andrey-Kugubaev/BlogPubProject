from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from django import forms

from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Группа теста',
            slug='group_test',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост тестовый',
            group=cls.group,
            image=cls.uploaded
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
        cache.clear()
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
        cache.clear()
        response = self.guest_client.get(reverse('posts:posts_list'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Пост тестовый')
        self.assertEqual(post_group_0, 'Группа теста')
        #self.assertEqual(post_image_0, self.uploaded)

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


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='Группа с комментом',
            slug='group_test_com',
            description='Описание группы для комментирования',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост тестовый для комментов',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = CommentTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_create(self):
        # после успешной отправки комментарий появляется на странице поста.
        post = CommentTests.post
        data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=data
        )
        self.assertEqual(Comment.objects.count(), 1)
        check = Comment.objects.first()
        self.assertEqual(check.text, 'Тестовый комментарий')
        self.assertEqual(check.post, self.post)
        self.assertEqual(check.author, self.user)


class CashTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_cashuser')
        #cls.group = Group.objects.create(
        #    title='Группа с комментом для кэша',
        #    slug='group_test_cash',
        #    description='Описание группы для теста кэша',
        #)
        #cls.post = Post.objects.create(
        #    author=cls.user,
        #    text='Пост тестовый для кэша',
        #    group=cls.group,
        #)

    def setUp(self):
        self.guest_client = Client()
        self.user = CashTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cash_index(self):
        response = self.authorized_client.get(reverse('posts:posts_list'))
        cashe_text = 'Новый текст'
        Post.objects.create(author=CashTests.user, text=cashe_text)
        response = self.authorized_client.get(reverse('posts:posts_list'))
        self.assertNotContains(response, cashe_text)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:posts_list'))
        self.assertContains(response, cashe_text)
        Post.objects.filter(pk=1).delete()
        response = self.authorized_client.get(reverse('posts:posts_list'))
        self.assertContains(response, cashe_text)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:posts_list'))
        self.assertNotContains(response, cashe_text)

    def tearDown(self):
        cache.clear()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='testauthor')
        cls.user = User.objects.create_user(username='testuser')
        cls.user_un = User.objects.create_user(username='testuserunfol')
        cls.group = Group.objects.create(
            title='Тест подписов',
            slug='group_test_fol',
            description='Описание группы для теста подписок',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тест подписки',
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.user_client = Client()
        self.user_unfollow_client = Client()
        self.user = FollowTests.user
        self.author = FollowTests.author
        self.user_un = FollowTests.user_un
        self.author_client.force_login(self.author)
        self.user_client.force_login(self.user)
        self.user_unfollow_client.force_login(self.user_un)

    def test_auth_follow(self):
        self.user_client.get(reverse('posts:profile_follow', args=[self.author.username]))
        response = self.user_client.get(reverse('posts:follow_index'))
        self.assertEqual(Follow.objects.count(), 1)
        check = Follow.objects.first()
        self.assertEqual(check.user, self.user)
        self.assertEqual(check.author, self.author)

    def test_auth_unfollow(self):
        self.lion = Follow.objects.create(user=self.user, author=self.author)
        self.user_client.get(
            reverse('posts:profile_unfollow', args=[self.author.username])
            )
        self.assertEqual(Follow.objects.count(), 0)

    def test_post_follow(self):
        post = FollowTests.post
        self.user_client.get(
            reverse('posts:profile_follow', args=[self.author.username])
            )
        response = self.user_client.get(reverse('posts:follow_index'))
        self.assertContains(response, post.text)

    def test_post_unfollow(self):
        post = FollowTests.post
        response = self.user_unfollow_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, post.text)
