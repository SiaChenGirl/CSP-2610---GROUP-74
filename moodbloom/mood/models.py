from django.db import models
from django.contrib.auth.models import User

# 1. 用户资料表
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

# 2. 心情记录表
class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=True, blank=True) 
    mood_name = models.CharField(max_length=50, null=True, blank=True) 
    intensity = models.IntegerField(default=3) 
    content = models.TextField(blank=True) 
    song = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.mood_name}"

# 3. 心理健康资源表 (由 Admin 负责上传 Link)
class Article(models.Model):
    CATEGORY_CHOICES = [
        ('Sleep', 'Better Sleep'),
        ('Stress', 'Stress Relief'),
        ('Self-Love', 'Self-Love'),
        ('Focus', 'Deep Focus'),
        ('Anxiety', 'Anxiety'),
        ('Exercise', 'Exercise'),
        ('Hydration', 'Hydration'),
        ('Social', 'Social'),
        ('Gratitude', 'Gratitude'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Sleep')
    summary = models.CharField(max_length=500, blank=True) # 简介
    external_url = models.URLField(max_length=500, null=True, blank=True) # 文章链接
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"

# 4. 反馈记录表
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True) 
    rating = models.IntegerField(default=0)
    email = models.EmailField(null=True, blank=True)
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Guest'}"
    
    