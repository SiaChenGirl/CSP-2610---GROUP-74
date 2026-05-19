from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot/', views.forgot_view, name='forgot'),
    
    path('mainpage/', views.mainpage_view, name='mainpage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('moodentry/', views.moodentry_view, name='moodentry'),
    
    path('article/', views.article_view, name='article'),
    path('api/articles/', views.get_articles_by_category, name='api_articles'), # 核心 API
    
    path('feedback/', views.feedback_view, name='feedback'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('search/', views.search_view, name='search'),
]