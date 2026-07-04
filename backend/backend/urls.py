"""
URL configuration for backend project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from users import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')), 
    path('check-session/', views.check_session, name='check_session'),
    path('diaryhistory/', views.diary_history_view, name='diaryhistory'), 
    path('admin-login/', views.admin_login_page_view, name='admin_login_page'),
    path('admin-login-url/', views.admin_login_view, name='admin_login_url'),
    path('admin-portal/', views.admin_portal_view, name='admin_portal'),
    path('article-admin/', views.article_admin_view, name='article_admin'),
]

# 核心修改：让静态文件在生产环境(DEBUG=False)也能工作
urlpatterns += staticfiles_urlpatterns()

# 媒体文件（用户上传）依然保持在 DEBUG 下
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)