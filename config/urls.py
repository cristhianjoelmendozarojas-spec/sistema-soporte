from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.forms.urls')),
    path('admin-site/', include('apps.users.urls')),
    path('colaboradores/', include('apps.employees.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
