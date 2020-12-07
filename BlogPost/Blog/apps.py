from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _



class BlogConfig(AppConfig):
    name = 'Blog'

class ProfilesConfig(AppConfig):
    name = 'Blog'
    verbose_name = _('profiles')

    def ready(self):
        import Blog.signals