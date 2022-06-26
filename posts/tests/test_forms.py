import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Post, Group

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuserform')
        cls.group = Group.objects.create(
            title='Группа теста формы',
            slug='f_group_test',
            description='Описание группы для формы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста формы',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = PostFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост для теста формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            #follow=True
        )
        self.assertRedirects(response, '/profile/testuserform/')
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(Post.objects.filter(text='Тестовый пост для теста формы', group=self.group.id).exists()) #image='posts/small.gif'))

    def test_edit_post(self):
        posts_count = Post.objects.count()
        new_text = 'Тестовый пост для теста редактирования'
        form_data = {
            'text': new_text,
            'group': self.group.id,
            #'image': uploaded,
        }
        self.authorized_client.post(reverse('posts:post_edit', kwargs={'post_id': self.post.id}), data=form_data)
        post = PostFormTests.post
        post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertIn(new_text, post.text)
