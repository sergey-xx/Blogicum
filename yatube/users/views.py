from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    """Класс отображения формы регистрации"""
    form_class = CreationForm
    success_url = reverse_lazy('post:index')
    template_name = 'users/signup.html'


def password_change_form(request):
    """Форма смены пароля"""
    template = 'users/password_change_form.html'
    return render(request, template)


def password_reset_form(request):
    """"Форма сброса забытого пароля"""
    template = 'users/password_reset_form.html'
    return render(request, template)


def password_reset_done(request):
    """Отображает страницу успешного сброса пароля"""
    template = 'users/password_reset_done.html'
    return render(request, template)
