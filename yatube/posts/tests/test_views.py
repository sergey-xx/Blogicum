from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
# from django.views.defaults import page_not_found, permission_denied
from core.views import page_not_found

from posts.models import Group, Post, Comment
from django.conf import settings

User = get_user_model()


class PostsPagesTests(TestCase):
    """Тестирование view-функций приложения"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
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
            content_type='image/gif')

        cls.post = Post.objects.create(
            author=cls.author,
            text='12345678901234567890',
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author = cls.author,
            text = 'Тестовый комментарий',
            post = cls.post
        )

        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.POST_REVERSE_URL = reverse('posts:post_edit',
                                       kwargs={'post_id': cls.post.id})

        cls.GROUP_LIST_URL = reverse('posts:group_list',
                                     kwargs={'slug': cls.group.slug})

        cls.AUTHOR_PROFILE_URL = reverse('posts:profile',
                                         kwargs={'username':
                                                 cls.author.username})

        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})
        
        cls.PAGE_404 = '/non_existing/'
        cls.INDEX_URL = reverse('posts:index')
        cls.ABOUT_TECH_URL = reverse('about:tech')
        cls.ABOUT_AUTHOR_URL = reverse('about:author')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.LOGIN_URL = reverse('users:login')
        cls.FOLLOW_INDEX_URL: reverse('posts:follow_index',
                                      kwargs={'post_id': cls.post.id})

    def setUp(self):
        """Создаем авторизованный клиент"""
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_use_correct_template(self):
        """view-функция использует верный шаблон """
        templates = {
            self.POST_CREATE_URL: 'posts/post_create_form.html',
            self.POST_REVERSE_URL: 'posts/post_create_form.html',
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.AUTHOR_PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.INDEX_URL: 'posts/index.html',
            self.ABOUT_TECH_URL: 'about/about_tech.html',
            self.ABOUT_AUTHOR_URL: 'about/about_author.html',
            self.LOGOUT_URL: 'users/logged_out.html',
            self.LOGIN_URL: 'users/login.html',
            self.PAGE_404: 'core/404.html',
            self.FOLLOW_URL: 'posts/follow.html'
        }
        for url, template in templates.items():
            with self.subTest(f'Приложение {url} использует шаблон {template}',
                              url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        post_text = first_post.text
        post_author = first_post.author
        post_image = first_post.image
        index_page_data = {
            post_text: self.post.text,
            post_author: self.post.author,
            post_image: self.post.image,
        }
        for tested_data, ref_data in index_page_data.items():
            with self.subTest(tested_data=tested_data):
                self.assertEqual(tested_data, ref_data)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_LIST_URL)
        first_post = response.context['page_obj'][0]
        post_text = first_post.text
        post_author = first_post.author.username
        post_image = first_post.image

        group_list_data = {
            post_text: self.post.text,
            post_author: self.post.author.username,
            post_image: self.post.image,
        }
        for tested_data, ref_data in group_list_data.items():
            with self.subTest(tested_data=tested_data):
                self.assertEqual(tested_data, ref_data)

    def test_group_list_page_dont_show_incorrect_context(self):
        """Пост не попал не в ту группу."""
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )
        response_gr1_before = self.authorized_client.get(self.GROUP_LIST_URL)
        post_counter_gr1_before = \
            len(response_gr1_before.context['page_obj'].object_list)

        response_gr2_before = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': group_2.slug}))
        post_counter_gr2_before = \
            len(response_gr2_before.context['page_obj'].object_list)
        Post.objects.create(
            author=self.author,
            text='12345678901234567890',
            group=self.group
        )
        response_gr1_after = self.authorized_client.get(self.GROUP_LIST_URL)
        post_counter_gr1_after = \
            len(response_gr1_after.context['page_obj'].object_list)
        response_gr2_after = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': group_2.slug}))
        post_counter_gr2_after = \
            len(response_gr2_after.context['page_obj'].object_list)
        self.assertEqual(post_counter_gr1_after, post_counter_gr1_before + 1)
        self.assertEqual(post_counter_gr2_after, post_counter_gr2_before)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        first_post = response.context['post']
        post_amount = response.context['post_amount']
        post_text = first_post.text
        post_author = first_post.author.username
        post_image = first_post.image
        post_comment = first_post.comments.first()
        post_detail_data = {
            post_text: self.post.text,
            post_author: self.post.author.username,
            post_image: self.post.image,
            post_amount: 1,
            post_comment: self.post.comments.first()
        }
        for tested_data, ref_data in post_detail_data.items():
            with self.subTest(tested_data=tested_data):
                self.assertEqual(tested_data, ref_data)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.AUTHOR_PROFILE_URL)
        first_post = response.context['page_obj'][0]
        profile_author_name = response.context['author'].username
        profile_post_amount = response.context['post_amount']
        post_amount = response.context['post_amount']
        post_text = first_post.text
        post_author = first_post.author.username
        post_image = first_post.image
        profile_posts_data = {
            post_text: self.post.text,
            post_author: self.post.author.username,
            post_amount: 1,
            profile_author_name: self.post.author.username,
            post_image: self.post.image,
            profile_post_amount: 1,
        }
        for tested_data, ref_data in profile_posts_data.items():
            with self.subTest(tested_data=tested_data):
                self.assertEqual(tested_data, ref_data)

    def test_cache(self):
        """Проверка, что пост остается в кэше при удалении из базы"""
        response_0 = self.authorized_client.get(self.INDEX_URL)
        Post.objects.all().delete()
        response_1 = self.authorized_client.get(self.INDEX_URL)
        self.assertEqual(response_0.content, response_1.content)
        cache.clear()
        response_2 = self.authorized_client.get(self.INDEX_URL)
        self.assertNotEqual(response_0.content, response_2.content)

    def test_follow(self):
        response_0 = self.authorized_client.get(self.INDEX_URL)

    def test_unfollow(self):
        pass



class PaginatorViewTest(TestCase):
    """Тестирование паджинатора"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts_amount = settings.POSTS_ON_PAGE + settings.POSTS_ON_PAGE // 2

        objs = (Post(text=f'Test {i}',
                author=cls.author, group=cls.group)
                for i in range(cls.posts_amount))
        Post.objects.bulk_create(objs)

        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_LIST_URL = reverse('posts:group_list',
                                     kwargs={'slug': cls.group.slug})

        cls.AUTHOR_PROFILE_URL = reverse('posts:profile',
                                         kwargs={'username':
                                                 cls.author.username})
        cls.tested_urls = [
            cls.INDEX_URL,
            cls.AUTHOR_PROFILE_URL,
            cls.GROUP_LIST_URL, ]

    def setUp(self):
        """Создаем авторизованный клиент"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_index_first_page_contains_ten_records(self):
        """Проверяем, что первая страница содержит все посты"""
        for url in self.tested_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POSTS_ON_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Проверяем, что вторая страница содержит половину постов"""
        for url in self.tested_urls:
            with self.subTest(url=url):
                response = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.posts_amount % settings.POSTS_ON_PAGE)
