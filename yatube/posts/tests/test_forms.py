import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Comment
from django.conf import settings


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.author,
            text='12345678901234567890',
            group=cls.group)
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый комментарий',
            post=cls.post)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем авторизованный клиент"""
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Создание поста авторизованным пользователем"""
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
        form_data = {'text': 'some_text2',
                     'group': self.group.id,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        url = reverse('posts:profile', kwargs={'username':
                                               self.post.author.username})
        self.assertRedirects(response, url)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, self.group.id)
        self.assertEqual(post.author.id, self.author.id)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Редактирование поста авторизованным автором"""
        post_count = Post.objects.count()
        form_data = {'text': 'some_text2',
                     'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id':
                                                       self.post.id}))
        post = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author.id, self.author.id)

    def test_not_create_post(self):
        """Невозможность создания поста неавторизованным пользователем"""
        post_count = Post.objects.count()
        form_data = {'text': 'some_text2',
                     'group': self.group.id}
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        expected_redirect = (reverse('users:login') + '?next='
                             + reverse('posts:post_create'))
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Post.objects.count(), post_count)

    def test_comment_post(self):
        """Возможность создания комментария авторизованным пользователем"""
        comments_count = self.post.comments.all().count()
        data = {'text': 'Тестовый комментарий 2'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=data)
        last_comment = self.post.comments.last()
        self.assertEqual(comments_count + 1, self.post.comments.all().count())
        self.assertEqual(last_comment.text, data['text'])
        self.assertEqual(last_comment.author, self.author)

    def test_not_comment_post(self):
        """Невозможность создания комментария неавторизованным пользователем"""
        comments_count = self.post.comments.all().count()
        data = {'text': 'Тестовый комментарий 2'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=data)
        self.assertEqual(comments_count, self.post.comments.all().count())
        expected_redirect = (reverse('users:login') + '?next='
                             + reverse('posts:add_comment',
                                       kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, expected_redirect)
