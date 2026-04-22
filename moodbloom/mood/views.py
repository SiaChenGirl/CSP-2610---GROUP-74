from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Mood  # 导入你的所有表
import json

# 1. 登录页面 + 登录逻辑
@csrf_exempt
def login_view(request):
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