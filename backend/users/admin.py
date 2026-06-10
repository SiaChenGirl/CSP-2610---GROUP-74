from django.contrib import admin

from .models import (
    Profile,
    MoodEntry,
    MoodPhoto,
    Article,
    Favorite,
<<<<<<< HEAD
    Feedback,
    Music
=======
    Feedback
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
)


# Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birthday', 'email_verified')
    search_fields = ('user__username',)


# Mood Entry
@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'category',
        'mood',
        'intensity',
        'created_at'
    )

    list_filter = (
        'category',
        'created_at'
    )

    search_fields = (
        'user__username',
        'mood',
        'diary_text'
    )


# Mood Photo
@admin.register(MoodPhoto)
class MoodPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'mood_entry',
        'uploaded_at'
    )


# Feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subject',
        'email',
        'rating',
        'created_at'
    )

    list_filter = (
        'rating',
        'created_at'
    )

    search_fields = (
        'subject',
        'message'
    )


# Article
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'created_at'
    )

    search_fields = (
        'title',
        'summary',
        'content'
    )


# Favorite
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'article'
<<<<<<< HEAD
    )


# Music Library
@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'mood_category'
    )

    list_filter = (
        'mood_category',
    )

    search_fields = (
        'title',
=======
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
    )