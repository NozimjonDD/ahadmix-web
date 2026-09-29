from pathlib import Path

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.i18n import set_language
from django.views.static import serve

# from .swagger_conf import swagger_urlpatterns

# Base templates directory (where index.html lives)
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Non-i18n URL patterns
urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('set-language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    # path('ckeditor/', include('ckeditor_uploader.urls')),
]

# i18n URL patterns
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
)

urlpatterns += [
    path("api/", include('apps.api.urls')),
]

# urlpatterns += swagger_urlpatterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve /assets/ and /data/ from the templates/ directory (dev convenience,
# so index.html's relative paths work without any template-tag changes).
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^assets/(?P<path>.*)$', serve,
                {'document_root': _TEMPLATES_DIR / 'assets'}),
        re_path(r'^data/(?P<path>.*)$', serve,
                {'document_root': _TEMPLATES_DIR / 'data'}),
    ]
