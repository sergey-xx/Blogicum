from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='12345678901234567890', )

        cls.INDEX_URL = '/'
        cls.GROUP_URL = f'/group/{cls.group.slug}/'
        cls.ABOUT_TECH_URL = '/about/tech/'
        cls.ABOUT_AUTHOR_URL = '/about/author/'
        cls.POST_DETAILS_URL = f'/posts/{cls.post.id}/'
        cls.AUTHOR_PROFILE_URL = f'/profile/{cls.post.author.username}/'
        cls.GROUP_POSTS_URL = f'/group/{cls.group.slug}/'
        cls.LOGAUT_URL = '/auth/logout/'
        cls.LOGIN_URL = '/auth/login/'
        cls.PASSWORD_CHANGE_URL = '/auth/password_change/'
        cls.CREATE_URL = '/create/'
        cls.POST_EDIT_URL = f'/posts/{cls.post.id}/edit/'

        cls.FREE_TO_ACCES_URLS = [
            cls.INDEX_URL,
            cls.GROUP_URL,
            cls.ABOUT_TECH_URL,
            cls.ABOUT_AUTHOR_URL,
            cls.POST_DETAILS_URL,
            cls.AUTHOR_PROFILE_URL,
            cls.GROUP_POSTS_URL,
            # cls.LOGAUT_URL,
            # cls.LOGIN_URL,
            ]

        cls.AUTHORITHATION_REQUIRED_URLS = [
            cls.PASSWORD_CHANGE_URL,
            cls.CREATE_URL,
            cls.POST_EDIT_URL]

    def setUp(self):
        # Создаем неавторизованый клиент
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов ."""
        for tested_url in self.FREE_TO_ACCES_URLS:
            with self.subTest(tested_url=tested_url):
                response = self.guest_client.get(tested_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user(self):
        """Проверка доступа авторизованным пользователем ."""
        for tested_url in self.AUTHORITHATION_REQUIRED_URLS:
            with self.subTest(tested_url=tested_url):
                response = self.authorized_client.get(tested_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_not_exists_and_return_404(self):
        """Проверка 404 несуществующих адресов ."""
        response = self.guest_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_redirect_anonymous_on_login(self):
        """Проверка переадресации незалогиненого пользователя"""
        redirected_urls = {
            self.CREATE_URL: self.LOGIN_URL + '?next=' + self.CREATE_URL,
            self.POST_EDIT_URL: self.LOGIN_URL + '?next=' + self.POST_EDIT_URL,
            self.PASSWORD_CHANGE_URL: (self.LOGIN_URL
                                       + '?next='
                                       + self.PASSWORD_CHANGE_URL)}
        for tested_url, expected_redirect in redirected_urls.items():
            with self.subTest(expected_redirect=expected_redirect):
                response = self.guest_client.get(tested_url, follow=True)
                self.assertRedirects(response, expected_redirect)

    def test_home_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон..."""
        templates = {
            self.INDEX_URL: 'posts/index.html',
            self.ABOUT_TECH_URL: 'about/about_tech.html',
            self.ABOUT_AUTHOR_URL: 'about/about_author.html',
            self.POST_DETAILS_URL: 'posts/post_detail.html',
            self.AUTHOR_PROFILE_URL: 'posts/profile.html',
            self.GROUP_POSTS_URL: 'posts/group_list.html',
            self.LOGAUT_URL: 'users/logged_out.html',
            self.LOGIN_URL: 'users/login.html', }

        for url, template in templates.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
