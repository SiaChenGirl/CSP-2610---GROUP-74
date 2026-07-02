from users.models import Favorite, Article
from django.contrib.auth.models import User

count = 0

for old in Favorite.objects.using("sqlite").all():
    new_user = User.objects.get(username=old.user.username)
    new_article = Article.objects.get(title=old.article.title)

    Favorite.objects.get_or_create(
        user=new_user,
        article=new_article,
    )

    count += 1

print(f"Copied {count} Favorite records!")