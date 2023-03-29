from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.cache import cache_page

from django.conf import settings
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm


def pagination(request, some_objs, obj_on_page):
    """Возвращает выбранное количество постов на странице"""
    paginator = Paginator(some_objs, obj_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def group_posts(request, slug):
    """Отображает все посты выбранной группы"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts, settings.POSTS_ON_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(20, key_prefix='index_page')
def index(request):
    """Отображает посты в хронологическом порядке"""
    posts = Post.objects.all()
    page_obj = pagination(request, posts, settings.POSTS_ON_PAGE)
    context = {'page_obj': page_obj, }
    template = 'posts/index.html'
    return render(request, template, context)


def profile(request, username):
    """Отображает все посты пользователя"""
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author=author)
    post_amount = posts.count()
    page_obj = pagination(request, posts, settings.POSTS_ON_PAGE)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author__exact=author)
    )
    context = {'page_obj': page_obj,
               'author': author,
               'post_amount': post_amount,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    """Позволяет создавать новые посты и выбирать теги"""
    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        return render(request, 'posts/post_create_form.html', {'form': form})

    form.instance.author = request.user
    form.save()
    return redirect(
        reverse('posts:profile', kwargs={'username': request.user.username})
    )


def post_detail(request, post_id):
    """Отображает полный текст поста и детали"""
    post = get_object_or_404(Post, id=post_id)
    post_amount = (
        Post.objects.select_related('author').
        filter(author=post.author).count())
    form = CommentForm(request.POST or None)
    context = {'post': post,
               'post_amount': post_amount,
               'comments': post.comments.all(),
               'form': form}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create_form.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Выводит посты авторов на которых подписан пользователь"""
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, posts, settings.POSTS_ON_PAGE)
    context = {'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    author = get_object_or_404(User, username=username)
    if author != request.user:
        follow, created = Follow.objects.get_or_create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
