from users.models import MoodPhoto, MoodEntry

count = 0

for old in MoodPhoto.objects.using("sqlite").all():

    new_entry = MoodEntry.objects.filter(
        user__username=old.mood_entry.user.username,
        entry_date=old.mood_entry.entry_date,
        mood=old.mood_entry.mood,
    ).last()

    MoodPhoto.objects.create(
        mood_entry=new_entry,
        image=old.image,
        uploaded_at=old.uploaded_at,
    )

    count += 1

print(f"Copied {count} MoodPhoto records!")