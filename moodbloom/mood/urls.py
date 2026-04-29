from django.urls import path
from . import views  # 从当前文件夹导入 views.py

urlpatterns = [
    path('', views.login_view, name='login'),      # 首页
    path('register/', views.register, name='register'), # 注册页
    path('dashboard/', views.dashboard, name='dashboard'), # 仪表盘
]
path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),