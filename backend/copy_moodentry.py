from users.models import MoodEntry, Music
from django.contrib.auth.models import User

count = 0

for old in MoodEntry.objects.using("sqlite").all():
    new_user = User.objects.get(username=old.user.username)

    new_music = None
    if old.selected_music:
        try:
            new_music = Music.objects.get(title=old.selected_music.title)
        except Music.DoesNotExist:
            pass

    MoodEntry.objects.create(
        user=new_user,
        mood=old.mood,
        category=old.category,
        diary_text=old.diary_text,
        intensity=old.intensity,
        selected_music=new_music,
        created_at=old.created_at,
        entry_date=old.entry_date,
    )

    count += 1

print(f"Copied {count} MoodEntry records!")