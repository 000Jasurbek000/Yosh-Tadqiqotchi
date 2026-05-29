"""
URL configuration for xalikova_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as media_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

# Media fayllarni uzatish.
# DEBUG=True bo'lganda Django'ning standart static() yordamchisi ishlaydi.
# Productionda (DEBUG=False) static() bo'sh ro'yxat qaytaradi, shuning uchun
# SERVE_MEDIA=True bo'lganda media fayllarni to'g'ridan-to'g'ri serve qilamiz.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif getattr(settings, 'SERVE_MEDIA', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
