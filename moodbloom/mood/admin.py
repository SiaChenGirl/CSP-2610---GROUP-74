from django.contrib import admin
from .models import Mood, Profile, Article, Feedback

# 1. Profile 配置：查看用户基本资料
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'birthday')
    search_fields = ('user__username',)

# 2. Mood 配置：核心心情记录
class MoodAdmin(admin.ModelAdmin):
    # list_display 控制在列表页显示的列
    list_display = ('user', 'category', 'mood_name', 'intensity', 'created_at')
    # list_filter 在右侧增加筛选框，方便按日期或心情大类查找
    list_filter = ('category', 'created_at')
    # search_fields 增加搜索框，可以搜用户名或日记内容
    search_fields = ('user__username', 'content', 'mood_name')

# 3. Feedback 配置：查看用户建议
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'email', 'created_at')
    list_filter = ('rating', 'created_at')

# 4. Article 配置：心理健康文章管理
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')

# 统一注册
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Mood, MoodAdmin)