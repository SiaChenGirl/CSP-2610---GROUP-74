from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class  MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20)
    diary_text = models.TextField(blank=True, null=True)
    intensity = models.IntegerField(null=True, blank=True)
    song_title = models.CharField(max_length=255, null=True, blank=True)
    artist = models.CharField(max_length=255, null=True, blank=True)
    music_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MoodPhoto(models.Model):
    mood_entry = models.ForeignKey(MoodEntry, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='mood_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
