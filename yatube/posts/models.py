from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Имя группы', max_length=200)
    slug = models.SlugField('Слаг группы', max_length=20, unique=True)
    description = models.TextField('Описание группы', null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'image',
        upload_to='posts/',
        blank=True,
        null=True
    )

    is_liked = False
    like_amount = None

    def __str__(self) -> str:
        return self.text[:settings.SHORT_POST_LENGTH]

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария',
                            help_text='Введите текст комментария')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_following'
        )]

class Like(models.Model):
    user = models.ForeignKey(
        User,
        related_name='liker',
        on_delete=models.CASCADE,
        
    )

    post = models.ForeignKey(
        Post,
        related_name='post_like',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'post'],
            name='unique_like'
        )]