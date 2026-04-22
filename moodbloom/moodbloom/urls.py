from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mood.urls')),  # 这一行会去调用 mood 文件夹里的 urls.py
]