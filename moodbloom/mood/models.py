from django.db import models
from django.contrib.auth.models import User

# 1. 用户资料表 (用于存储性别等额外信息)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# 2. 心情记录表 (核心功能)
class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_type = models.CharField(max_length=20)
    description = models.TextField()
    intensity = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mood_type}"

# 3. 心理健康文章表 (Optional Feature)
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # 还可以加一个创建时间，方便排序
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title