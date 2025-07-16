"""
URL configuration for archive_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# map_project/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from archive_app.views import map_view, get_markers, file_list, download_file

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_view, name='map_view'),
    path('get_markers/', get_markers, name='get_markers'),
    path('files/', file_list, name='file_list'),
    path('download/', download_file, name='download_file'),
]

# 開発環境でメディアファイルと静的ファイルを配信するための設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)