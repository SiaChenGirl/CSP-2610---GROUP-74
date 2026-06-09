from django.contrib import admin
from .models import Mood, Profile, Article

admin.site.register(Mood)
admin.site.register(Profile)
admin.site.register(Article) # 注册新表