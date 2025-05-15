# yt_downloader/urls.py
from django.contrib import admin
from django.urls import path
from downloader import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/info/', views.get_video_info),
]