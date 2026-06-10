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
<<<<<<< HEAD
from django.conf import settings

# 导入合并后的新模型
from .models import Profile, MoodEntry, MoodPhoto, Favorite, Article, Feedback, Music
=======

# 导入合并后的新模型
from .models import Profile, MoodEntry, MoodPhoto, Favorite, Article, Feedback
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411

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
<<<<<<< HEAD
        Profile.objects.create(user=user, gender=gender, email_verified=False)

        # views2 强大的邮件验证系统
        verify_link = f"http://127.0.0.1:8000/verify-email/{username}/"
        
        try:
        
            send_mail(
                'Verify your MoodBloom account',
                f'''
                Welcome to MoodBloom 🌸
                Click the link below to verify your email:
            
                {verify_link}
                ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )

        except Exception as e:
            print("Email Error:", e)

        return JsonResponse({
            'message': 'Registration successful. Please verify your email.'
        })

=======
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
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
    return render(request, 'register.html')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
<<<<<<< HEAD

        user = authenticate(
            request,
            username=data.get('username'),
            password=data.get('password')
        )

        if user:

            profile = Profile.objects.get(user=user)

            if not profile.email_verified:
                return JsonResponse({
                    'error': 'Please verify your email before logging in.'
                }, status=403)

            login(request, user)

            return JsonResponse({
                'message': 'OK'
            })

        return JsonResponse({
            'error': 'Invalid username or password'
        }, status=400)

=======
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'status': 'OK'})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
    return render(request,'email_verified.html')
=======
    return JsonResponse({'message': 'Email verified successfully'})
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411


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
<<<<<<< HEAD

    if request.method == 'POST':
        
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        
    
        profile.gender = request.POST.get('gender')
        profile.birthday = request.POST.get('birthday') or None
        
    
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES.get('avatar')
            
        profile.save()
        return redirect('profile') 
        
=======
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        profile.gender = request.POST.get('gender')
        profile.birthday = request.POST.get('birthday') or None
        profile.save()
        return redirect('profile') 
        
    # 如果是 AJAX 请求，返回 JSON（支持 views2）
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'gender': profile.gender,
<<<<<<< HEAD
            'birthday': str(profile.birthday) if profile.birthday else None,
            'avatar': profile.avatar.url if profile.avatar else None
=======
            'birthday': str(profile.birthday) if profile.birthday else None
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
        })
    return render(request, 'profile.html', {'profile': profile})


<<<<<<< HEAD

=======
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
        # 💡 这里改为使用 request.POST.get 而不是 json.loads
        mood = request.POST.get('mood') or request.POST.get('mood_name')
        if not mood:
            return JsonResponse({'error': 'Mood is required'}, status=400)
            
        diary = request.POST.get('diary_text') or request.POST.get('content')
        category = request.POST.get('category')
        intensity = request.POST.get('intensity', 3)
        music_id = request.POST.get('music_id')

        selected_music = None
        if music_id:
            try:
                selected_music = Music.objects.get(id=music_id)
            except Music.DoesNotExist:
                pass
     

        # 1. 创建 MoodEntry，确保 user=request.user (实现数据隔离)
        entry = MoodEntry.objects.create(
            user=request.user, 
            mood=mood, 
            category=category, 
            diary_text=diary, 
            intensity=intensity, 
            selected_music=selected_music
        )
        
        # 2. 核心：处理照片上传，关联到刚才创建的 entry
        # 前端 <input type="file" name="photos" multiple> 对应的就是 'photos'
        if request.FILES.getlist('photos'):
            for file in request.FILES.getlist('photos'):
                MoodPhoto.objects.create(mood_entry=entry, image=file)
                
        return JsonResponse({'status': 'success', 'message': 'Mood entry saved successfully!'})
    
    return render(request, 'moodentry.html')

=======
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


>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
def get_music_library(request):
    music_list = Music.objects.all()

    data = []

    for music in music_list:
        data.append({
            "id": music.id,
            "title": music.title,
            "mood_category": music.mood_category,
            "audio_file": music.audio_file.url
        })

    return JsonResponse(data, safe=False)


@login_required
def gallery_view(request):
    # 既能渲染网页，也能提供数据
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # 优化查询：使用 select_related 提升性能，并按时间倒序
        photos = MoodPhoto.objects.filter(mood_entry__user=request.user)\
                                  .select_related('mood_entry')\
                                  .order_by('-mood_entry__created_at')
        
        gallery = []
        for photo in photos:
            # 增加安全检查，确保 image 存在
            if photo.image:
                gallery.append({
                    'image': photo.image.url, 
                    'mood': photo.mood_entry.mood, 
                    'date': photo.mood_entry.created_at.strftime('%Y-%m-%d')
                })
        
        return JsonResponse({'photos': gallery})
    
    # 渲染网页时，确保只传该用户的 entries
    return render(request, 'gallery.html', {
        'moods': MoodEntry.objects.filter(user=request.user).order_by('-created_at')
    })
=======
def gallery_view(request):
    # 既能渲染网页，也能提供数据
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        photos = MoodPhoto.objects.filter(mood_entry__user=request.user).order_by('-mood_entry__created_at')       
        gallery = [{'image': photo.image.url, 'mood': photo.mood_entry.mood, 'date': photo.mood_entry.created_at.strftime('%Y-%m-%d')} for photo in photos]
        return JsonResponse({'photos': gallery})
    return render(request, 'gallery.html', {'moods': MoodEntry.objects.filter(user=request.user)})

>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411

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

<<<<<<< HEAD
=======

>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
# ==========================================
# 4. 心理健康文章与收藏夹模块 (支持前端动态卡片点击获取分类数据)
# ==========================================

@login_required
def article_view(request):
<<<<<<< HEAD
    # 1. 恢复它！让它继续渲染你的中转选择页
    return render(request, 'article.html')


@login_required
def paragraph_view(request):
    # 2. 新增这个！专门用来渲染具体看文章的三栏主网页
    return render(request, 'paragraph.html')


@login_required
def favourite_page_view(request):
    # 3. 保持这个！专门用来渲染收藏夹卡片页
    return render(request, 'favourite.html')

=======
    return render(request, 'article.html')


>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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

<<<<<<< HEAD
# ✨ 完美安全修改：移除了 @csrf_exempt 以免文件流冲突，加入了 request.POST 和 request.FILES 的处理机制
@login_required
def feedback_view(request):
    if request.method == 'POST':
        try:
            # 💡 因为前端用了 FormData，所以用 request.POST 替代 json.loads(request.body)
            subject = request.POST.get('subject', 'General Feedback')
            rating = request.POST.get('rating')
            # 完美兼容：获取前端传来的 content 并与你数据库的 message 绑定
            message = request.POST.get('content') or request.POST.get('message')
            email = request.POST.get('email', request.user.email)

            # ✨ 核心功能：接住前端传过来的图片文件
            screenshot = request.FILES.get('screenshot')

            if not rating or not message:
                return JsonResponse({'status': 'error', 'message': 'Rating and content are required.'})

            # 插入并保存到数据库（message 完美对齐你的数据库字段）
            Feedback.objects.create(
                user=request.user, 
                subject=subject, 
                rating=int(rating), 
                message=message,
                email=email,
                screenshot=screenshot  # 成功保存图片路径到数据库，图片落入 media/feedback/
            )
            return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully.'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # GET 请求时，保持原样渲染 feedback.html
=======
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
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
        if not frequent_mood:
            frequent_mood = {
                'mood': 'No Data',
                'total': 0
            }
=======
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411

        percentage_data = []
        for item in mood_counts:
            percentage = (item['total'] / total_entries) * 100 if total_entries > 0 else 0
            percentage_data.append({'mood': item['mood'], 'percentage': round(percentage, 2)})

        trend_data = moods.values('created_at__date', 'mood').annotate(total=Count('id')).order_by('created_at__date')

<<<<<<< HEAD
        recommendation = (
            "🌱 Your moods appear balanced. "
            "Keep tracking your emotions and maintaining healthy daily habits."
        )       
        
        sorted_data = sorted(
            percentage_data,
            key=lambda x: x['percentage'],
            reverse=True
        )

        for item in sorted_data:
            mood = item['mood'].lower()
            percentage = item['percentage']

            if mood == 'sad' and percentage >= 50:
                recommendation = (
                    "😔 You have been feeling sad quite often recently. "
                    "Consider taking some time to rest, talk with someone you trust, "
                    "or explore our wellness articles."
                )
                break

            elif mood == 'angry' and percentage >= 40:
                recommendation = (
                    "😠 You seem to be experiencing a lot of frustration lately. "
                    "Try relaxation techniques, deep breathing, or activities "
                    "that help reduce stress."
                )
                break

            elif mood == 'neutral' and percentage >= 60:
                recommendation = (
                    "😐 You have been feeling neutral most of the time. "
                    "This may be a good opportunity to explore new interests, "
                    "set personal goals, or engage in activities that bring you joy."
                )
                break

            elif mood == 'happy' and percentage >= 60:
                recommendation = (
                    "😊 Great job! You've been feeling positive most of the time. "
                    "Keep up the habits and activities that contribute to your happiness."
                )
                break

   

=======
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
            'longest_streak': longest_streak,
            'recommendation': recommendation,
=======
            'longest_streak': longest_streak
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
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
<<<<<<< HEAD
    return render(request, 'forgot.html')
=======
    return render(request, 'forgot.html')
    

        
    
>>>>>>> 1cbb4dcdde624d2e18ef2ed65720fe1bf840b411
