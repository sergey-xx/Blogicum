from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.cache import cache

from ..models import Group, Post
from django.conf import settings

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='12345678901234567890',
        )
    def setUp(self):
        """Очищаем кэш"""
        cache.clear()
        
    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_str = {
            self.group.__str__: self.group.title,
            self.post.__str__: self.post.text[:settings.SHORT_POST_LENGTH], }
        for field, value in field_str.items():
            with self.subTest(field=field):
                self.assertEqual(field(), value)
