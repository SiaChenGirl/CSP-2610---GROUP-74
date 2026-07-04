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
from users import views 
from users.views import admin_login_view, admin_portal_view  # 这一行必须存在
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # 只要这一个 include 即可！不要在下面粘贴 users.urls 的内容
    path('', include('users.urls')), 

    path('check-session/', views.check_session, name='check_session'),
    
    path('diaryhistory/', views.diary_history_view, name='diaryhistory'), 
    path('admin/', admin.site.urls),
    # 修改路径引用方式为 views.函数名
    path('admin-login/', views.admin_login_page_view, name='admin_login_page'),
    path('admin-login-url/', views.admin_login_view, name='admin_login_url'),
    path('admin-portal/', views.admin_portal_view, name='admin_portal'),
    path('article-admin/', views.article_admin_view, name='article_admin'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
    if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)