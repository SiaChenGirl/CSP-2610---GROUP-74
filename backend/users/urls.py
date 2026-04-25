from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('api/register/', views.register),
    path('api/login/', views.user_login),
    path('api/logout/', views.user_logout),
    path('api/profile/', views.user_profile),
    path('api/change-password/', views.change_password),
    path(
    'api/password-reset/',
    auth_views.PasswordResetView.as_view(),
    name='password_reset'
    ),

    path(
        'api/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'
    ),

    path(
        'api/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    path(
        'api/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    path('verify-email/<str:username>/', views.verify_email),
]