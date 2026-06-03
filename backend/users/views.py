import json
from datetime import timedelta, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db.models import Q, Count, Avg, DateField
from django.db.models.functions import Cast, TruncMonth

# 导入合并后的新模型
from .models import Profile, MoodEntry, MoodPhoto, Favorite, Article, Feedback

# ==========================================
# 1. 身份验证与账户管理模块 (融合 views2 的邮件验证与 views1 的模板跳转)
# ==========================================

@csrf_exempt
def register_view(request): 
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        gender = data.get('gender', 'Others')

        if User.objects.filter(username=username).exists():
             return JsonResponse({'error': 'Username already exists'}, status=400)

        if User.objects.filter(email=email).exists():
             return JsonResponse({'error': 'Email already exists'}, status=400)

        # 创建用户并同步创建 Profile
        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user, gender=gender)

        # views2 强大的邮件验证系统
        verify_link = f"http://127.0.0.1:8000/verify-email/{username}/"
        try:
            send_mail(
                'Verify your MoodBloom account',
                f'Click this link to verify your email:\n{verify_link}',
                'admin@moodbloom.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

        return JsonResponse({'message': 'User created successfully', 'status': 'OK'})
    return render(request, 'register.html')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'status': 'OK'})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    return render(request, 'login.html')


@csrf_exempt
@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'})
    # 兼容旧系统的 GET 请求直接退出
    logout(request)
    return redirect('login')


def verify_email(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    profile.email_verified = True
    profile.save()
    return JsonResponse({'message': 'Email verified successfully'})


@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        user = request.user

        if not user.check_password(old_password):
            return JsonResponse({"error": 'Old password is incorrect'}, status=400)
        
        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return JsonResponse({'message': 'Password change successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        profile.gender = request.POST.get('gender')
        profile.birthday = request.POST.get('birthday') or None
        profile.save()
        return redirect('profile') 
        
    # 如果是 AJAX 请求，返回 JSON（支持 views2）
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'gender': profile.gender,
            'birthday': str(profile.birthday) if profile.birthday else None
        })
    return render(request, 'profile.html', {'profile': profile})


# ==========================================
# 2. 心情记录与相册模块 (融合 views1 与 views2 的多字段录入)
# ==========================================

@login_required
def mainpage_view(request): 
    return render(request, 'mainpage.html')


@csrf_exempt
@login_required
def moodentry_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # 完美揉合：既兼容 views1 字段，又首选 views2 核心字段
        mood = data.get('mood') or data.get('mood_name')

        if not mood:
            return JsonResponse(
                {'error': 'Mood is required'},
                status=400
            )
        diary = data.get('diary_text') or data.get('content')
        category = data.get('category')
        intensity = data.get('intensity', 3)
        
        # 音乐字段兼容
        song_title = data.get('song_title') or data.get('song')
        artist = data.get('artist')
        music_link = data.get('music_link')

        MoodEntry.objects.create(
            user=request.user,
            mood=mood,
            category=category,
            diary_text=diary,
            intensity=intensity,
            song_title=song_title,
            artist=artist,
            music_link=music_link
        )
        return JsonResponse({'status': 'success', 'message': 'Mood entry saved successfully!'})
    return render(request, 'moodentry.html')


@login_required
def today_mood(request):
    today = now().date()
    latest = MoodEntry.objects.filter(user=request.user, created_at__date=today).order_by('-created_at').first()
    if latest:
        return JsonResponse({"mood": latest.mood})
    return JsonResponse({"message": "No mood today. Please add a mood."})


@csrf_exempt
@login_required
def upload_photo(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(MoodEntry, id=entry_id, user=request.user)
        for file in request.FILES.getlist('photos'):
            MoodPhoto.objects.create(mood_entry=entry, image=file)
        return JsonResponse({'message': 'Photos uploaded successfully!'})
    return JsonResponse({'error': 'Invalid request.'}, status=400)


@login_required
def gallery_view(request):
    # 既能渲染网页，也能提供数据
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        photos = MoodPhoto.objects.filter(mood_entry__user=request.user).order_by('-mood_entry__created_at')       
        gallery = [{'image': photo.image.url, 'mood': photo.mood_entry.mood, 'date': photo.mood_entry.created_at.strftime('%Y-%m-%d')} for photo in photos]
        return JsonResponse({'photos': gallery})
    return render(request, 'gallery.html', {'moods': MoodEntry.objects.filter(user=request.user)})


# ==========================================
# 3. 搜索与探索模块
# ==========================================

@login_required
def search_view(request):
    # 如果带有搜索条件，返回筛选过的 JSON 结果列表（views2 的智能搜索）
    if request.GET.get('q') or request.GET.get('mood') or request.GET.get('date'):
        query = request.GET.get('q')
        mood = request.GET.get('mood')
        entry_date = request.GET.get('date')
        sort = request.GET.get('sort')

        results = MoodEntry.objects.filter(user=request.user)
        if query:
            results = results.filter(diary_text__icontains=query)
        if mood:
            results = results.filter(mood=mood)
        if entry_date:
            results = results.filter(created_at__date=entry_date)

        if sort == "latest":
            results = results.order_by('-created_at')
        elif sort == "oldest":
            results = results.order_by('created_at')

        data = [{"id": entry.id, "mood": entry.mood, "diary": entry.diary_text, "date": entry.created_at.strftime('%Y-%m-%d')} for entry in results]
        return JsonResponse({"message": "Success", "results": data})
        
    return render(request, 'search.html')


# ==========================================
# 4. 心理健康文章与收藏夹模块 (支持前端动态卡片点击获取分类数据)
# ==========================================

@login_required
def article_view(request):
    return render(request, 'article.html')


# 关键融合：views1 用于支持你和陈女孩前台页面异步点击的分类 API
@login_required
def get_articles_by_category(request):
    cat = request.GET.get('category')
    user = request.user
    
    # 如果是‘Anxiety’或‘Favourite Articles’收藏分类，联动 views2 的 Favorite 表
    if cat == 'Favorites':
        favorites = Favorite.objects.filter(user=user)

        data = [{
            'id': f.article.id,
            'title': f.article.title,
            'summary': f.article.summary,
            'external_url': f.article.external_url,
            'favorited': True
        } for f in favorites]

        return JsonResponse(data, safe=False)

    # 正常的分类过滤，抓取合并模型中保留的摘要与外部链接
    articles = Article.objects.filter(category=cat)
    data = []
    for a in articles:
        is_favorited = Favorite.objects.filter(user=user, article=a).exists()
        data.append({
            "id": a.id,
            "title": a.title,
            "summary": a.summary,
            "content": a.content,
            "external_url": a.external_url,
            "favorited": is_favorited
        })
    return JsonResponse(data, safe=False)


@login_required
def add_favorite(request, article_id):
    user = request.user
    article = get_object_or_404(Article, id=article_id)
    Favorite.objects.get_or_create(user=user, article=article)
    return JsonResponse({"message": "Added to favorites"})


@login_required
def remove_favorite(request, article_id):
    user = request.user
    try:
        fav = Favorite.objects.get(user=user, article_id=article_id)
        fav.delete()
        return JsonResponse({"message": "Removed from favorites"})
    except Favorite.DoesNotExist:
        return JsonResponse({"message": "Not in favorites"})


# ==========================================
# 5. 反馈管理与数据仪表盘模块 (集成 views2 的高效 Streak 算法)
# ==========================================

@csrf_exempt
@login_required
def feedback_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = data.get('subject', 'General Feedback')
        rating = data.get('rating')
        # 兼容 views1 的 content 命名与 views2 的 message 命名
        message = data.get('message') or data.get('content')
        email = data.get('email', request.user.email)

        Feedback.objects.create(
            user=request.user, 
            subject=subject, 
            rating=rating, 
            message=message,
            email=email
        )
        return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully.'})
    return render(request, 'feedback.html')


@login_required
def dashboard_view(request):
    # 如果是 AJAX 异步拉取，返回 views2 算好的高级图表数据、打卡 Streak
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        moods = MoodEntry.objects.filter(user=request.user)
        mood_counts = moods.values('mood').annotate(total=Count('id'))
        total_entries = moods.count()

        monthly_distribution = moods.annotate(month=TruncMonth('created_at')).values('month', 'mood').annotate(total=Count('id')).order_by('month')
        frequent_mood = moods.values('mood').annotate(total=Count('id')).order_by('-total').first()

        percentage_data = []
        for item in mood_counts:
            percentage = (item['total'] / total_entries) * 100 if total_entries > 0 else 0
            percentage_data.append({'mood': item['mood'], 'percentage': round(percentage, 2)})

        trend_data = moods.values('created_at__date', 'mood').annotate(total=Count('id')).order_by('created_at__date')

        # 高级自适应连续打卡 (Streak System)
        dates = moods.order_by('-created_at').values_list('created_at__date', flat=True).distinct()
        current_streak = 0
        if dates:
            today = date.today()
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
            for d in reversed(dates):
                if previous_date is None:
                    temp_streak = 1
                elif d == previous_date + timedelta(days=1):
                    temp_streak += 1
                else:
                    temp_streak = 1
                longest_streak = max(longest_streak, temp_streak)
                previous_date = d

        return JsonResponse({
            'total_moods': list(mood_counts),
            'percentage_distribution': percentage_data,
            'monthly_distribution': list(monthly_distribution),
            'trend_over_time': list(trend_data),
            'most_frequent_mood': frequent_mood,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        })

    # 默认浏览器访问渲染原汁原味的 HTML Dashboard，并传输趋势参数
    user_moods = MoodEntry.objects.filter(user=request.user)
    distribution = list(user_moods.values('mood').annotate(count=Count('id')))
    trends_query = user_moods.annotate(date_only=Cast('created_at', DateField())).values('date_only').annotate(avg_intensity=Avg('intensity')).order_by('date_only')
    trends_list = [{'created_at__date': str(i['date_only']), 'avg_intensity': float(i['avg_intensity'])} for i in trends_query]
    
    return render(request, 'dashboard.html', {
        'moods': user_moods.order_by('-created_at'), 
        'mood_distribution_json': json.dumps(distribution), 
        'mood_trends_json': json.dumps(trends_list)
    })


def forgot_view(request): 
    return render(request, 'forgot.html')
    

        
    