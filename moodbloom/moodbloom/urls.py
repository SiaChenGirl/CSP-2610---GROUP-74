from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # 进入后台的路径
    path('', include('mood.urls')), # 关键：这一行会把请求导向 mood 里的 urls.py
]