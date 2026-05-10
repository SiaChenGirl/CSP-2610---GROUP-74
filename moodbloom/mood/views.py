<<<<<<< HEAD
from django.shortcuts import render
from django.contrib.auth.models import User
=======
import json
from django.shortcuts import render, redirect
>>>>>>> b471e3d (combine frontend html and backend)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
from .models import Profile, Mood  # 导入你的所有表
import json

# 1. 登录页面 + 登录逻辑
=======
from django.contrib import messages
from .models import Profile, Mood, Article, Feedback

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


# --- 2. 身份验证逻辑 (关键点) ---

>>>>>>> b471e3d (combine frontend html and backend)
@csrf_exempt
def login_view(request):
    """
    处理登录逻辑：
    GET: 访问 http://127.0.0.1:8000/ (根目录) 时显示登录页面
    POST: 处理来自 login.html 的 AJAX 登录请求
    """
    # 如果用户已经登录，访问根目录时直接重定向到主页
    if request.user.is_authenticated and request.method == 'GET':
        return redirect('mainpage')

    if request.method == 'POST':
<<<<<<< HEAD
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid username or password'})
    
    # 如果是平时访问，就显示你队友做的那个 login 网页
    # 确认一下你的文件名是 index.html 还是 login.html
    return render(request, 'index.html') 

# 2. 注册逻辑
@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender', 'Others')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'})

        # 这里就是存入数据库的关键！
        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user, gender=gender)

        return JsonResponse({'message': 'User created successfully'})
    
    # 如果直接访问 /register/ 路径，显示注册网页
    return render(request, 'register.html')

# 3. 登出
@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    return JsonResponse({'error': 'Invalid request'})

# 4. 仪表盘（占位）
@login_required
def dashboard(request):
    return render(request, 'dashboard.html') # 假设以后有这个页面
def register(request):
    if request.method == 'POST':
        # ... 这里是处理注册数据的代码 ...
        pass
    
    # 这一行最重要！它决定了你访问 /register/ 时看到哪个网页
    return render(request, 'register.html')
=======
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # 这个 'Login successful' 字符串必须和 login.html JS 里的判断一致
                return JsonResponse({'message': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Data error: ' + str(e)}, status=400)
            
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    # 登出后跳转回根目录，即登录页面
    return redirect('login')


def register_view(request): 
    return render(request, 'register.html')


def forgot_view(request): 
    return render(request, 'forgot.html')


# --- 3. 主页及功能页面 (全部受登录保护) ---

@login_required
def mainpage_view(request):
    """只有点击登录按钮并通过验证后，才能跳转到这里"""
    return render(request, 'mainpage.html')


@login_required
def feedback_view(request):
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
    moods = Mood.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'moods': moods})


@login_required
def gallery_view(request): 
    return render(request, 'gallery.html')


@login_required
def search_view(request): 
    return render(request, 'search.html')
>>>>>>> b471e3d (combine frontend html and backend)
