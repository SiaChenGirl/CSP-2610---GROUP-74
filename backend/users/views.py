from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Profile, MoodEntry, MoodPhoto, Feedback
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils.timezone import now
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
    