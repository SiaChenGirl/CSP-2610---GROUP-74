from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 必须是空字符串，这样才能把 http://127.0.0.1:8000/ 交给子路由处理
    path('', include('mood.urls')), 
]