import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Mood, Article, Feedback
from django.contrib.auth.models import User

# --- 1. 核心 Profile 逻辑 ---

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        profile.gender = request.POST.get('gender')
        birthday_val = request.POST.get('birthday')
        profile.birthday = birthday_val if birthday_val else None
        profile.save()

        messages.success(request, "Profile updated successfully! 💜")
        return redirect('profile') 

    return render(request, 'profile.html', {'profile': profile})


# --- 2. 身份验证逻辑 ---

@csrf_exempt
def login_view(request):
    """处理登录逻辑"""
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('mainpage')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Data error: ' + str(e)}, status=400)
            
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def register_view(request): 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            gender = data.get('gender', 'Others')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, gender=gender)
            return JsonResponse({'message': 'User created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return render(request, 'register.html')

def forgot_view(request): 
    return render(request, 'forgot.html')

def verify_email(request, uidb64, token):
    return render(request, 'login.html', {'message': 'Email verified!'})


# --- 3. 主页及功能页面 ---

@login_required
def mainpage_view(request):
    return render(request, 'mainpage.html')

@login_required
def feedback_view(request):
    # 修改：增加保存 Feedback 的 POST 逻辑
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Feedback.objects.create(
                user=request.user,
                subject=data.get('subject', 'General Feedback'),
                rating=data.get('rating', 0),
                email=request.user.email, # 自动获取登录用户的 email
                content=data.get('content', '')
            )
            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'feedback.html')

@login_required
def article_view(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'article.html', {'articles': articles})

@login_required
def moodentry_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Mood.objects.create(
                user=request.user,
                category=data.get('category'),
                mood_name=data.get('mood_name'),
                intensity=data.get('intensity', 3),
                content=data.get('content', ''), 
                song=data.get('song', '')
            )
            return JsonResponse({'status': 'success', 'message': 'Mood bloomed!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'moodentry.html')

@login_required
def dashboard_view(request): 
    # 获取当前用户的所有记录
    moods = Mood.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'moods': moods})

@login_required
def gallery_view(request): 
    return render(request, 'gallery.html')

@login_required
def search_view(request): 
    return render(request, 'search.html')