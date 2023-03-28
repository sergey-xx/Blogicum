from django.views.generic.base import TemplateView


class AuthorPage(TemplateView):
    template_name = 'about/about_author.html'


class TechPage(TemplateView):
    template_name = 'about/about_tech.html'
