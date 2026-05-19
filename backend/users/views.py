from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from .models import Profile, MoodEntry, MoodPhoto, Feedback
=======
from .models import Profile, MoodEntry, MoodPhoto, Favorite, Article
>>>>>>> 1cf0bc72941d20ebf3d074c5b54b690a57de2e66
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db.models import Q, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from datetime import timedelta, date
import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user, gender=gender)

        verify_link = f"http://127.0.0.1:8000/verify-email/{username}/"

        print("sending email now")
        send_mail(
            'Verify your MoodBloom account',
            f'Click this link to verify your email:\n{verify_link}',
            'admin@moodbloom.com',
            [email],
            fail_silently=False,
        )

        return JsonResponse({'message': 'User created successfully'})

    return JsonResponse({'error': 'Invalid request'})


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid username or password'})

    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    
    return JsonResponse({'error': 'Invalid request'})

@login_required
def user_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'gender': profile.gender
    })

@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        user = request.user

        if not user.check_password(old_password):
            return JsonResponse({
                "error": 'Old password is incorrect'
            })
        
        user.set_password(new_password)
        user.save()

        return JsonResponse({
            'message': 'Password change sucessfully.'
        })
    
    return JsonResponse({
        'error': 'Invalid request'
    })

def verify_email(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    profile.email_verified = True
    profile.save()

    return JsonResponse({
        'message': 'Email verified successfully'
    })

@csrf_exempt
@login_required
def add_mood(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        mood = data.get('mood')
        diary = data.get('diary_text')
        intensity = data.get('intensity')
        song_title = data.get('song_title')
        artist = data.get('artist')
        music_link = data.get('music_link')

        MoodEntry.objects.create(
            user=request.user,
            mood=mood,
            diary_text=diary,
            intensity=intensity,
            song_title=song_title,
            artist=artist,
            music_link=music_link
        )

        return JsonResponse({
            'message': 'Mood entry saved successfully!'
        })
    
    return JsonResponse({
        'error': 'Invalid request.'
    })

@login_required
def today_mood(request):
    today = now().date()

    latest = MoodEntry.objects.filter(
        user=request.user,
        created_at__date=today
    ).order_by('-created_at').first()

    if latest:
        return JsonResponse({
            "mood": latest.mood
        })
    
    return JsonResponse({
        "message": "No mood today. Please add a mood."
    })

@csrf_exempt
@login_required
def upload_photo(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(MoodEntry, id=entry_id, user=request.user)

        for file in request.FILES.getlist('photos'):
            MoodPhoto.objects.create(
                mood_entry=entry,
                image=file
            )

            return JsonResponse({
                'message': 'Photos uploaded successfully!'
            })
        
        return JsonResponse({
            'error': 'Invalid request.'
        })
<<<<<<< HEAD

@login_required
def photo_gallery(request):
    photos = MoodPhoto.objects.filter(
        mood_entry__user=request.user
    ).order_by('-mood_entry__created_at')       

    gallery = []

    for photo in photos:
        gallery.append({
            'image': photo.image.url,
            'mood': photo.mood_entry.mood,
            'date': photo.mood_entry.created_at.strftime('%Y-%m-%d')
        })

    return JsonResponse({
        'photos': gallery
    })

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        rating = data.get('rating')
        message = data.get('message')
        feedback = Feedback.objects.create(
            user = request.user,
            rating = rating,
            message = message
        )

        return JsonResponse({
            'message': 'Feedback submitted successfully.'
        })
    
    return JsonResponse({
        'error': 'Invalid request.'
    }, status=400)
=======
    
def search_entries(request):
    query = request.GET.get('q')
    mood = request.GET.get('mood')
    date = request.GET.get('date')
    sort = request.GET.get('sort')

    results = MoodEntry.objects.all()

    if query:
        results = results.filter(
            diary_text__icontains=query
        )

    if mood:
        results = results.filter(
            mood=mood
        )

    if date:
        results = results.filter(
            created_at__date=date
        )

    if sort == "latest":
        results = results.order_by('-created_at')
    elif sort == "oldest":
        results = results.order_by('created_at')

    data = []
    for entry in results:
        data.append({
            "id": entry.id,
            "mood": entry.mood,
            "diary": entry.diary_text,
            "date": entry.created_at
        })

    if not data:
        return JsonResponse({
        "message": "No results found",
        "results": []
    })

    return JsonResponse({
    "message": "Success",
    "results": data
    })

@login_required
def get_articles(request):
    user = request.user
    articles = Article.objects.all()

    data = []
    for a in articles:
        is_favorited = Favorite.objects.filter(user=user, article=a).exists()

        data.append({
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "favorited": is_favorited
        })

    return JsonResponse(data, safe=False)

@login_required
def add_favorite(request, article_id):
    user = request.user

    article = Article.objects.get(id=article_id)

    Favorite.objects.get_or_create(user=user, article=article)

    return JsonResponse({"message": "Added to favorites"})

@login_required
def get_favorites(request):
    user = request.user

    favorites = Favorite.objects.filter(user=user)

    data = []
    for f in favorites:
        data.append({
            "id": f.article.id,
            "title": f.article.title,
            "content": f.article.content
        })

    return JsonResponse(data, safe=False)


@login_required
def remove_favorite(request, article_id):
    user = request.user

    try:
        fav = Favorite.objects.get(user=user, article_id=article_id)
        fav.delete()
        return JsonResponse({"message": "Removed from favorites"})
    except Favorite.DoesNotExist:
        return JsonResponse({"message": "Not in favorites"})
    

def search_articles(request):
    query = request.GET.get('q')

    articles = Article.objects.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    data = []
    for a in articles:
        data.append({
            "id": a.id,
            "title": a.title,
            "content": a.content
        })

    return JsonResponse(data, safe=False)


@login_required
def dashboard_status(request):
    moods = MoodEntry.objects.filter(user=request.user)
    # Total mood count
    mood_counts = moods.values('mood').annotate(
        total=Count('id')
    )
    # Total entries
    total_entries = moods.count()

    # Percentage distribution
    monthly_distribution = moods.annotate(
        month=TruncMonth('created_at')
    ).values(
        'month',
        'mood'
    ).annotate(
        total=Count('id')
    ).order_by('month')

    frequent_mood = moods.values('mood').annotate(
        total=Count('id')
    ).order_by('-total').first()

    percentage_data = []
    for item in mood_counts:
        percentage = (item['total'] / total_entries) * 100 if total_entries > 0 else 0
        percentage_data.append({
            'mood': item['mood'],
            'percentage': round(percentage, 2)
        })

    # Mood trend over time
    trend_data = moods.values(
        'created_at__date',
        'mood'
    ).annotate(
        total=Count('id')
    ).order_by('created_at__date')

    # Streak System
    dates = moods.order_by('-created_at').values_list(
        'created_at__date',
        flat=True
    ).distinct()

    current_streak = 0
    if dates:
        today = dates.today()

        for entry_date in dates:
            if entry_date == today:
                current_streak += 1
                today = today - timedelta(days=1)
            else:
                break
    longest_streak = 0
    temp_streak = 0

    if dates:
        previous_date = None

        for date in reversed(dates):
            if previous_date is None:
                temp_streak = 1
            elif date == previous_date + timedelta(days=1):
                temp_streak += 1
            else:
                temp_streak = 1

            longest_streak = max(longest_streak, temp_streak)

            previous_date = date



    return JsonResponse({
        'total_moods': list(mood_counts),
        'percentage_distribution': percentage_data,
        'monthly_distribution': list(monthly_distribution),
        'trend_over_time': list(trend_data),
        'most_frequent_mood': frequent_mood,
        'current_streak': current_streak,
        'longest_streak': longest_streak
    })

    
    

        
>>>>>>> 1cf0bc72941d20ebf3d074c5b54b690a57de2e66
    