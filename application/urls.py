from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
import sys

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("questions.urls")),
    path("", include("core.urls")),
]

_debug_urls = (
    settings.DEBUG
    and not (len(sys.argv) > 1 and sys.argv[1] == "test")
)
if _debug_urls:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
        *urlpatterns,
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Администрирование сайта"
admin.site.site_title = "Админка"
