from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 核心页面渲染
    path('', views.login_view, name='login'), # 根路径跳转到登录页
    path('login/', views.login_view, name='login_page'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('mainpage/', views.mainpage_view, name='mainpage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    path('article/', views.article_view, name='article'),
    path('article/paragraph/', views.paragraph_view, name='paragraph'),
    path('article/favourite/', views.favourite_page_view, name='favourite'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
    path('feedback/', views.feedback_view, name='feedback'),

    # API 接口
    path('api/register/', views.register_view),
    path('api/logout/', views.user_logout),
    path('api/profile/', views.profile_view),
    path('api/change-password/', views.change_password),
    path('verify-email/<str:username>/', views.verify_email),
    path('add-mood/', views.moodentry_view),
    path('today-mood/', views.today_mood),
    path('search-entries/', views.search_view),
    path('upload-photo/<int:entry_id>/', views.upload_photo),
    path('api/photo-gallery/', views.gallery_view),
    path('api/articles/', views.get_articles_by_category, name='api_articles'),
    path('api/favorite/<int:article_id>/', views.add_favorite),
    path('api/unfavorite/<int:article_id>/', views.remove_favorite),
    path('api/feedback/', views.feedback_view),
    path('api/dashboard-status/', views.dashboard_view),

    # 密码重置相关
    path('forgot/', views.forgot_view, name='forgot'),
    path('api/password-reset/', views.forgot_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_complete.html'), name='password_reset_complete'),
]