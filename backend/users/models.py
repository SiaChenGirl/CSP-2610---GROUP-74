from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. 用户资料表 (以 Model 2 为主，保留验证和性别，融合 Model 1 的生日)
# ==========================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, blank=True, null=True) # 采用 Model 2 长度，设为允许空白兼容注册
    birthday = models.DateField(null=True, blank=True)             # 融入 Model 1 的生日字段
    email_verified = models.BooleanField(default=False)          # 保留 Model 2 邮件验证核心

<<<<<<< HEAD
# ✨ 增加这个头像字段，用于在 Profile 页面上传和显示图片
    # upload_to='avatars/' 会自动在你的 MEDIA_ROOT 下创建一个 avatars 文件夹
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
   
=======
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
    def __str__(self):
        return self.user.username


# ==========================================
# 2. 心情记录表 (以 Model 2 MoodEntry 为主结构，完美融合 Model 1 的歌单和分类逻辑)
# ==========================================
class MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20)                         # Model 2 核心心情字段 (对应 Model 1 mood_name)
    category = models.CharField(max_length=20, null=True, blank=True) # 融入 Model 1 的分类，方便前端过滤
    diary_text = models.TextField(blank=True, null=True)           # Model 2 核心日记字段 (对应 Model 1 content)
    intensity = models.IntegerField(default=3, null=True, blank=True) # 保留默认权重 3 
    
    # 音乐模块：完美融合 Model 1 的单字段与 Model 2 的详细字段
<<<<<<< HEAD
    selected_music = models.ForeignKey(
        'Music',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
=======
    song_title = models.CharField(max_length=255, null=True, blank=True) # 对应 Model 1 的 song 字段
    artist = models.CharField(max_length=255, null=True, blank=True)
    music_link = models.URLField(null=True, blank=True)
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # 融入 Model 1 的时间倒序排列，让日记历史按最新时间显示

    def __str__(self):
        return f"{self.user.username} - {self.mood}"


# ==========================================
# 3. 心情照片表 (完全保留 Model 2 的相册扩展功能)
# ==========================================
class MoodPhoto(models.Model):
    mood_entry = models.ForeignKey(MoodEntry, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='mood_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


# ==========================================
# 4. 心理健康资源表 (以 Model 2 结构为主，无缝融合 Model 1 的分类、简介和外部跳转链接)
# ==========================================
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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Sleep') # 融入分类，完美对接你前端的动态 API 抓取
    summary = models.CharField(max_length=500, blank=True)           # 融入 Model 1 简介
    content = models.TextField(blank=True, null=True)               # 保留 Model 2 内容字段
    external_url = models.URLField(max_length=500, null=True, blank=True) # 融入 Model 1 外部跳转链接，对接 Read More →
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"


# ==========================================
# 5. 文章收藏表 (完全保留 Model 2 收藏夹功能)
# ==========================================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"


# ==========================================
# 6. 用户反馈表 (以 Model 2 为主要结构，融合 Model 1 的主题和邮箱字段，去掉重复类)
# ==========================================
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # 允许为 Guest 匿名反馈
    subject = models.CharField(max_length=200, null=True, blank=True) # 融入 Model 1 意见主题
    email = models.EmailField(null=True, blank=True)               # 融入 Model 1 反馈者邮箱
    rating = models.IntegerField()                                  # Model 2 评分
    message = models.TextField()                                    # Model 2 反馈内容 (对应 Model 1 content)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
<<<<<<< HEAD
        return self.user.username if self.user else "Guest"
    
class Music(models.Model):
    title = models.CharField(max_length=100)
    mood_category = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='music/')

    def __str__(self):
        return self.title
=======
        return self.user.username if self.user else "Guest"
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
