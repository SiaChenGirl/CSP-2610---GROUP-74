from django.db import models
from django.contrib.auth.models import User

<<<<<<< HEAD
# 1. 用户资料表 (用于存储性别等额外信息)
=======
# 1. 用户资料表
>>>>>>> b471e3d (combine frontend html and backend)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

<<<<<<< HEAD
# 2. 心情记录表 (核心功能)
=======
# 2. 心情记录表
>>>>>>> b471e3d (combine frontend html and backend)
class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=True, blank=True)
    mood_name = models.CharField(max_length=50, null=True, blank=True)
    intensity = models.IntegerField(default=3)
    # 建议加上 blank=True，防止用户只选心情不写日记时报错
    content = models.TextField(blank=True) 
    song = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 这是一个好习惯：让数据默认按时间倒序排
        ordering = ['-created_at']

    def __str__(self):
        # 加上日期显示，方便你在后台辨认
        date_str = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else "No Date"
        return f"{self.user.username} - {self.mood_name} ({date_str})"

<<<<<<< HEAD
# 3. 心理健康文章表 (Optional Feature)
=======
# 3. 心理健康文章表
>>>>>>> b471e3d (combine frontend html and backend)
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    # 还可以加一个创建时间，方便排序
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
<<<<<<< HEAD
        return self.title
=======
        return self.title

# 4. 反馈记录表
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(default=0)
    email = models.EmailField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.email or 'Guest'}"
>>>>>>> b471e3d (combine frontend html and backend)
