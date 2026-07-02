from users.models import Feedback
from django.contrib.auth.models import User

count = 0

for old in Feedback.objects.using("sqlite").all():

    new_user = None
    if old.user:
        try:
            new_user = User.objects.get(username=old.user.username)
        except User.DoesNotExist:
            pass

    Feedback.objects.create(
        user=new_user,
        subject=old.subject,
        email=old.email,
        rating=old.rating,
        message=old.message,
        created_at=old.created_at,
    )

    count += 1

print(f"Copied {count} Feedback records!")