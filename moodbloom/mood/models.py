from django.db import models
from django.contrib.auth.models import User

# 1. 用户资料表 (存储性别、生日等额外信息)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


# 2. 心情记录表 (核心功能)
class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=True, blank=True) # 存储大类：happy, sad 等
    mood_name = models.CharField(max_length=50, null=True, blank=True) # 存储具体：lovely, tired 等
    intensity = models.IntegerField(default=3)
    content = models.TextField(blank=True) # 日记内容
    song = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 让数据默认按时间倒序排列，最新的在前面
        ordering = ['-created_at']

    def __str__(self):
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else "No Date"
        return f"{self.user.username} - {self.mood_name} ({date_str})"


# 3. 心理健康文章表
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 4. 反馈记录表
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # 增加 subject 字段，方便用户在页面填写主题
    subject = models.CharField(max_length=200, null=True, blank=True) 
    rating = models.IntegerField(default=0)
    email = models.EmailField(null=True, blank=True)
    content = models.TextField() # 具体的反馈意见
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.user.username if self.user else "Guest"
        return f"Feedback: {self.subject or 'No Subject'} (from {user_name})"