import json
import calendar
from datetime import timedelta, date
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db.models import Q, Count, Avg, DateField
from django.db.models.functions import Cast, TruncMonth, ExtractWeek, ExtractDay
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.views.decorators.cache import cache_control
from .models import Profile, MoodEntry, MoodPhoto, Favorite, Article, Feedback, Music
from calendar import monthrange
from collections import defaultdict
from django.contrib.auth.decorators import user_passes_test
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

        # 1. 严格的互斥检查：先查用户名
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'status': 'error', 
                'message': '👤Username already exists. Please choose another username.'
            }, status=400)

        # 2. 再查邮箱
        elif User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error', 
                'message': '📧Email already exists. Please use another email or log in.'
            }, status=400)

        # 3. 只有上面都不存在，才走创建逻辑
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            Profile.objects.create(user=user, gender=gender, email_verified=False)

            # 邮件发送系统
            verify_link = request.build_absolute_uri(reverse('verify_email', kwargs={'username': username}))
            # send_mail(
              #  'Verify your MoodBloom account',
               # f'Welcome to MoodBloom 🌸\n\nPlease verify your email:\n{verify_link}',
               # 'adminmoodbloom@gmail.com',
              #  [email],
               # fail_silently=False,
             # )

            # ✅ 成功返回：确保这里只返回这一句
            return JsonResponse({
                'status': 'success',
                'message': '🎉 Account created successfully! 📩 Please check your email and verify your account before logging in.'
            }, status=200)

    return render(request, 'register.html')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try: 
            user_obj = User.objects.get(username=username) 
        except User.DoesNotExist: 
            return JsonResponse({ 
                'error': '👤Account not found. Please register first.' 
            }, status=404)
    
        user = authenticate(request, username=username, password=password)
        if user is None: 
            return JsonResponse({ 
                'error': '❌Invalid username or password.' 
            }, status=400)

        try: 
            profile = Profile.objects.get(user=user) 
            if not profile.email_verified: 
                return JsonResponse({ 
                    'error': '📧Please verify your email before logging in.' 
                    }, status=403) 
                
        except Profile.DoesNotExist: 
            return JsonResponse({ 
                'error': 'Profile not found. Please contact support.' 
            }, status=400)
        
        login(request, user)
        return JsonResponse({ 
            'message': f'🌸Login successful. Welcome Back, {request.user.username}!', 
            'username': user.username 
        }, status=200)

    return render(request, 'login.html')


@csrf_exempt
@login_required
def user_logout(request):
    logout(request)
    # 强制让浏览器重定向，不要保留旧的历史记录
    return redirect('login')

def verify_email(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    profile.email_verified = True
    profile.save()
    return render(request,'email_verified.html')

@login_required
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_username = request.POST.get('username')

        # 1. 校验用户名是否已存在
        if User.objects.exclude(id=user.id).filter(username=new_username).exists():
            return JsonResponse({
                'error': 'Username already exists'
            }, status=400)

        # 2. 核心拦截：校验生日是否为未来日期
        birthday_str = request.POST.get('birthday')
        if birthday_str:
            try:
                # 将前端传来的 'YYYY-MM-DD' 字符串转换为 Python 的 date 对象
                birthday_date = date.fromisoformat(birthday_str)
                
                # 如果生日大于今天，直接拦截并报错
                if birthday_date > date.today():
                    # 兼容普通表单提交和 AJAX 提交
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'error': 'Birthday cannot be a future date'}, status=400)
                    
                    messages.error(request, "Oops! Birthday cannot be a future date.")
                    return render(request, 'profile.html', {
                        'profile': profile, 
                        'error': 'Birthday cannot be in the future.'
                    })
            except ValueError:
                # 防止传入非法日期格式字符串
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Invalid date format'}, status=400)
                return render(request, 'profile.html', {'profile': profile, 'error': 'Invalid date format.'})

        # 3. 校验通过，开始保存 User 基础信息
        user.username = new_username
        user.email = request.POST.get('email')
        user.save()
        
        # 4. 保存 Profile 扩展信息
        profile.gender = request.POST.get('gender')
        profile.birthday = birthday_str or None
        
        # 5. 处理头像上传
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES.get('avatar')
            
        profile.save()
        
        # 如果是 AJAX 提交则返回成功响应，如果是普通表单则重定向
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Profile updated successfully'})
            
        return redirect('profile') 
        
    # --- GET 请求逻辑 ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'gender': profile.gender,
            'birthday': str(profile.birthday) if profile.birthday else None,
            'avatar': profile.avatar.url if profile.avatar else None
        })
        
    return render(request, 'profile.html', {'profile': profile})

# ==========================================
# 2. 心情记录与相册模块 (融合 views1 与 views2 的多字段录入)
# ==========================================

@login_required 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def mainpage_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    entries = MoodEntry.objects.filter(user=request.user).order_by('-entry_date', '-created_at')
    
    latest_entry = entries.first()
    latest_photo_url = None
    
    if latest_entry:
        # 使用你在 models.py 中定义的 related_name='photos'
        latest_photo = latest_entry.photos.order_by('-id').first()
        if latest_photo and latest_photo.image:
            latest_photo_url = latest_photo.image.url
            
    # --- 【修正点】在这里定义 mood_data_json ---
    # 如果你没有特殊的图片命名规则，建议使用 entry.mood + ".png" 
    # 或者根据你的实际需求修改此处的逻辑
    mood_data_json = json.dumps({
        entry.entry_date.strftime('%Y-%m-%d'): entry.mood + ".png" 
        for entry in entries
    })
    # ------------------------------------------

    return render(request, 'mainpage.html', {
        'profile': profile,
        'entries': entries,
        'latest_photo_url': latest_photo_url,
        'latest_entry': latest_entry,
        'mood_data_json': mood_data_json # 现在这个变量已定义，不会报错了
    })

@csrf_exempt
@login_required(login_url='login') # 关键：确保未登录用户无法访问此接口，直接重定向到登录页
def moodentry_view(request):
    if request.method == 'POST':
        # 打印调试信息到终端，看看是谁在提交
        print(f"--- DEBUG: Current User Submitting Mood is: {request.user} ---")
        
        # 1. 双重安全检查
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'}, status=403)

        # 🌸 核心对齐：前端 FormData 传的是 'mood_name'，这里优先获取 'mood_name'
        mood = request.POST.get('mood_name') or request.POST.get('mood')
        if not mood:
            return JsonResponse({'status': 'error', 'message': 'Mood is required'}, status=400)
            
        # 🌸 核心对齐：前端传的是 'content'，这里优先获取 'content' 存入模型的 diary_text 字段
        diary = request.POST.get('content') or request.POST.get('diary_text') or ""
        category = request.POST.get('category')
        intensity = request.POST.get('intensity', 5) # 默认值跟前端 initial 保持一致 (5)
        
        # 🎵 歌曲处理：前端歌曲传的是整个 option 的 value（如 "song1.mp3|Song One|Singer A"）
        # 这里如果你使用的是特定的 Music Model 关联，需要特殊处理，这里先按你原本的逻辑获取
        music_id = request.POST.get('music_id') or request.POST.get('song') 
        selected_music = None
        if music_id and music_id.isdigit(): # 确保是 ID 时才查询
            try:
                selected_music = Music.objects.get(id=music_id)
            except Music.DoesNotExist:
                pass

        # 📅 日期安全转换：防止空字符串导致 Django 报错
        entry_date_str = request.POST.get('entry_date')
        if entry_date_str and entry_date_str.strip() != "":
            try:
                # 尝试将前端的各种字符串格式转为标准的 date 对象
                if "GMT" in entry_date_str or "T" in entry_date_str:
                    # 如果带时间戳，只截取前面的日期
                    entry_date = date.fromisoformat(entry_date_str.split('T')[0])
                else:
                    entry_date = date.fromisoformat(entry_date_str)
            except ValueError:
                entry_date = now().date() # 格式解析失败则降级为今天
        else:
            entry_date = now().date() # 前端没传或者传空，直接使用今天

        # 2. 写入数据库
        entry = MoodEntry.objects.create(
            user=request.user,  
            mood=mood,           # 完美保存心情名称 (例如: Happy, Kiss, Sick)
            category=category,   # 完美保存心情大类 (例如: happy, sad)
            diary_text=diary,    # 完美保存日记文本
            intensity=int(intensity), 
            selected_music=selected_music,
            entry_date=entry_date
        )
        
        # 3. 处理相册照片
        if request.FILES.getlist('photos'):
            for file in request.FILES.getlist('photos'):
                MoodPhoto.objects.create(mood_entry=entry, image=file)
                
        return JsonResponse({'status': 'success', 'message': 'Mood entry saved successfully!'})
    
    # --- GET 请求逻辑 ---
    selected_date = request.GET.get("date") or ""
    songs = Music.objects.all()
    return render(request, 'moodentry.html', { "selected_date": selected_date, "songs": songs, })



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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def gallery_view(request):
    # 既能渲染网页，也能提供数据
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # 优化查询：使用 select_related 提升性能，并按时间倒序
        photos = MoodPhoto.objects.filter(mood_entry__user=request.user)\
                                  .select_related('mood_entry')\
                                  .order_by('-mood_entry__entry_date')
        
        gallery = []
        for photo in photos:
            # 增加安全检查，确保 image 存在
            if photo.image:
                gallery.append({
                    'image': photo.image.url, 
                    'mood': photo.mood_entry.mood, 
                    'date': photo.mood_entry.entry_date.strftime('%Y-%m-%d')
                })
        
        return JsonResponse({'photos': gallery})
    
    # 渲染网页时，确保只传该用户的 entries
    return render(request, 'gallery.html', {
        'moods': MoodEntry.objects.filter(user=request.user).order_by('-entry_date')
    })


# ==========================================
# 4. 心理健康文章与收藏夹模块 (支持前端动态卡片点击获取分类数据)
# ==========================================



# 对所有页面执行相同的操作：article_view, gallery_view, profile_view, moodentry_view 等
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def article_view(request):
    # 1. 恢复它！让它继续渲染你的中转选择页
    return render(request, 'article.html')


@login_required
def paragraph_view(request):
    # 2. 新增这个！专门用来渲染具体看文章的三栏主网页
    return render(request, 'paragraph.html')


@login_required
def favourite_page_view(request):
    # 获取当前用户的所有收藏，并使用 select_related 优化数据库查询（连带取出 Article 对象）
    favorites = Favorite.objects.filter(user=request.user).select_related('article')
    return render(request, 'favourite.html', {'favorites': favorites})

@login_required
def get_articles_by_category(request):
    cat = request.GET.get('category')
    user = request.user
    
    # 收藏夹处理
    if cat == 'favorites':
        favorites = Favorite.objects.filter(user=user).select_related('article')
        data = [{
            'id': f.article.id,
            'title': f.article.title,
            'summary': f.article.summary,
            'external_url': f.article.external_url,
            'favorited': True
        } for f in favorites]
        return JsonResponse(data, safe=False)

    # 正常的分类过滤，直接用 'basics', 'motivation' 等 Key 查询
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


@csrf_exempt # 如果遇到 403 错误，加上这个装饰器测试一下
@login_required
def remove_favorite(request, article_id):
    user = request.user
    # 不管是否存在，只要请求了删除，就返回成功，这样前端可以放心移除卡片
    Favorite.objects.filter(user=user, article_id=article_id).delete()
    return JsonResponse({"message": "Removed from favorites"})

# ==========================================
# 5. 反馈管理与数据仪表盘模块
# ==========================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def feedback_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject', 'General Feedback')
            rating = data.get('rating')
            message = data.get('content')
            email = data.get('email', request.user.email)

            if not rating or not message:
                return JsonResponse({'status': 'error', 'message': 'Rating and content are required.'})

            Feedback.objects.create(
                user=request.user, 
                subject=subject, 
                rating=int(rating), 
                message=message,
                email=email
            )
            return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully.'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'feedback.html')

def check_session(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def dashboard_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # 1. 基础查询：当前用户的所有心情
        all_user_moods = MoodEntry.objects.filter(user=request.user)
        
        # 2. 月份过滤（只针对图表和百分比数据）
        selected_month = request.GET.get("month")
        if selected_month:
            year, month = selected_month.split("-")
            year = int(year)
            month = int(month)
        else:
            today = date.today()
            year = today.year
            month = today.month

        last_day = monthrange(year, month)[1]
        # 统一使用 entry_date 进行过滤
        moods = all_user_moods.filter(entry_date__year=year, entry_date__month=month)

        # 3. 基础统计
        mood_counts = moods.values('category').annotate(total=Count('id'))
        total_entries = moods.count()
        
        # 4. 每周分布统计
        weekly_entries = []
        for start_day in [1, 8, 15, 22, 29]:
            if start_day > last_day:
                break
            end_day = min(start_day + 6, last_day)
            count = moods.filter(entry_date__day__gte=start_day, entry_date__day__lte=end_day).count()
            weekly_entries.append({"label": f"{start_day}-{end_day}", "total": count })

        # 🔥【修复 1】解决 monthly_distribution 中包含 date 对象无法转 JSON 的问题
        monthly_distribution_query = moods.annotate(month=TruncMonth('entry_date')).values('month', 'mood').annotate(total=Count('id')).order_by('month')
        monthly_distribution = []
        for item in monthly_distribution_query:
            monthly_distribution.append({
                'month': item['month'].strftime('%Y-%m') if item['month'] else '',
                'mood': item['mood'],
                'total': item['total']
            })
        
        frequent_mood = moods.values('category').annotate(total=Count('id')).order_by('-total').first()
        if not frequent_mood:
            frequent_mood = {'category': 'No Data', 'total': 0}

        percentage_data = []
        for item in mood_counts:
            category_name = item['category'] or 'Unknown'
            percentage = (item['total'] / total_entries) * 100 if total_entries > 0 else 0
            percentage_data.append({'category': category_name, 'percentage': round(percentage, 2)})

        # 5. 情绪建议逻辑
        recommendation = (
            "No mood records were found for this period. "
            "Start tracking your moods to learn more about your emotional patterns."
        )
        
        sorted_data = sorted(percentage_data, key=lambda x: x['percentage'], reverse=True)
        if sorted_data and total_entries > 0:
            top_mood = sorted_data[0]['category'].lower()
            top_percentage = sorted_data[0]['percentage']

            if top_mood == "happy":
                recommendation = (
                    f"Happiness accounted for {top_percentage}% of your mood entries this month. "
                    "Your records suggest that positive emotions have been a significant part of your recent experiences. "
                    "Take time to appreciate the people, activities, and moments that contributed to these feelings."
                )
            elif top_mood == "sad":
                recommendation = (
                    f"Sadness accounted for {top_percentage}% of your mood entries this month. "
                    "Your mood records indicate that you may have been facing challenges recently. "
                    "Remember that difficult emotions are a normal part of life. Consider giving yourself time to rest."
                )
            elif top_mood == "angry":
                recommendation = (
                    f"Anger accounted for {top_percentage}% of your mood entries this month. "
                    "Strong emotions can often signal stress. Try taking short breaks, practicing deep breathing, or exercising."
                )
            elif top_mood == "neutral":
                recommendation = (
                    f"Neutral moods accounted for {top_percentage}% of your mood entries this month. "
                    "Periods of emotional stability can be valuable opportunities for reflection and personal growth."
                )

        # 6. 折线图数据处理
        trend_data = defaultdict(lambda: {"happy": 0, "sad": 0, "angry": 0, "neutral": 0 })
        for mood in moods:
            day = mood.entry_date
            category = (mood.category or "").lower()
            if category in trend_data[day]:
                trend_data[day][category] += 1

        # 🔥【修复 2】这里的 day 原本是 date 对象，必须转为 str(day) 避免底层格式序列化失败
        formatted_trend = []
        for day in sorted(trend_data.keys()):
            formatted_trend.append({
                "date": str(day),
                "happy": trend_data[day]["happy"],
                "sad": trend_data[day]["sad"],
                "angry": trend_data[day]["angry"],
                "neutral": trend_data[day]["neutral"],
            })
        
        # 7. Streak 算法
        dates = all_user_moods.order_by('-entry_date').values_list('entry_date', flat=True).distinct()

        current_streak = 0
        if dates:
            check_date = date.today()
            if dates[0] != check_date and dates[0] == check_date - timedelta(days=1):
                check_date = check_date - timedelta(days=1)
                
            for entry_date in dates:
                if entry_date == check_date:
                    current_streak += 1
                    check_date = check_date - timedelta(days=1)
                elif entry_date > check_date:
                    continue  
                else: 
                    break

        longest_streak = 0
        temp_streak = 1
        date_list = sorted(set(dates))
        if len(date_list) > 0:
            longest_streak = 1
            for i in range(1, len(date_list)):
                if (date_list[i] - date_list[i - 1]).days == 1:
                    temp_streak += 1
                elif (date_list[i] - date_list[i - 1]).days > 1:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
            longest_streak = max(longest_streak, temp_streak)

        # 返回安全的 JSON
        return JsonResponse({
            'total_moods': list(mood_counts),
            'percentage_distribution': percentage_data,
            'monthly_distribution': monthly_distribution, # 使用处理后的纯列表
            'trend_over_time': formatted_trend,
            'most_frequent_mood': frequent_mood,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'recommendation': recommendation,
            'weekly_entries': list(weekly_entries),
        })

    # --- GET 页面加载逻辑 ---
    user_moods = MoodEntry.objects.filter(user=request.user)
    distribution = list(user_moods.values('mood').annotate(count=Count('id')))
    trends_query = user_moods.annotate(date_only=Cast('entry_date', DateField())).values('date_only').annotate(avg_intensity=Avg('intensity')).order_by('date_only')
    trends_list = [{'created_at__date': str(i['date_only']), 'avg_intensity': float(i['avg_intensity'])} for i in trends_query]
    
    today = date.today()
    months = []
    for i in range(11, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
            
        last_day = monthrange(year, month)[1]
        months.append({
            "value": f"{year}-{month:02d}",
            "label": f"01 {datetime(year, month, 1).strftime('%b %Y')} - {last_day} {datetime(year, month, 1).strftime('%b %Y')}"
        })

    return render(request, 'dashboard.html', {
        'moods': user_moods.order_by('-entry_date'), 
        'mood_distribution_json': json.dumps(distribution), 
        'mood_trends_json': json.dumps(trends_list),
        'months': months,
        'current_month': today.strftime("%Y-%m")
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def search_view(request):
    # 获取前端传来的参数
    query = request.GET.get('q')        # 对应 keyword
    category = request.GET.get('category') # 核心修改：从获取 mood 改为获取 category
    entry_date = request.GET.get('date') # 对应 date
    
    if query or category or entry_date:
        results = MoodEntry.objects.filter(user=request.user)
        
        # 动态叠加过滤条件
        if query:
            results = results.filter(diary_text__icontains=query)
        if category:
            # 核心修改：改为过滤你的 category 字段，使用 iexact 忽略大小写
            results = results.filter(category__iexact=category) 
        if entry_date:
            results = results.filter(entry_date=entry_date)
            
        # 按时间倒序
        results = results.order_by('-entry_date', '-created_at')
        
        data = [{
            "id": entry.id, 
            "category": entry.category, # 返回 category 供前端展示或备用
            "mood": entry.mood, 
            "diary": entry.diary_text, 
            "date": entry.entry_date.strftime('%Y-%m-%d')
        } for entry in results]
        
        return JsonResponse({"message": "Success", "results": data})
        
    return render(request, 'search.html')

def forgot_view(request): 
    return render(request, 'forgot.html')

def custom_reset_view(request, uidb64, token):
    # 这里只是单纯渲染你的 reset.html
    # 并把 uidb64 和 token 传进去，以便你后续在 html 表单里用
    return render(request, 'reset.html', {'uid': uidb64, 'token': token})
 
@csrf_exempt
def forgot_password_action(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                'Reset your MoodBloom password',
                f'Click this link to reset your password: {reset_url}',
                'adminmoodbloom@gmail.com',
                [email],
                fail_silently=False,
            )
            # 修改这里：不再返回 JSON，而是告诉页面“成功了”
            return render(request, 'forgot.html', {'message': 'Check your email for the reset link!'})
        except User.DoesNotExist:
            # 也可以在这里传一个错误信息
            return render(request, 'forgot.html', {'error': 'Email not found'})
            
    return render(request, 'forgot.html')
# 2. 处理 reset.html 的提交（保存密码并跳回登录）
@csrf_exempt
def handle_password_save(request):
    if request.method == 'POST':
        uid = urlsafe_base64_decode(request.POST.get('uid')).decode()
        token = request.POST.get('token')
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            user.set_password(request.POST.get('new_password'))
            user.save()
            return redirect('login') # 成功后跳转回登录页
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
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

@csrf_exempt
def toggle_favorite(request, article_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Please login first.'}, status=403)

    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        
        # 查找是否存在该收藏记录
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, 
            article=article
        )

        if created:
            # 如果是刚创建的，代表这次操作是“添加收藏”
            return JsonResponse({'status': 'success', 'action': 'added'})
        else:
            # 如果记录已存在，则删除记录，代表这次操作是“取消收藏”
            favorite.delete()
            return JsonResponse({'status': 'success', 'action': 'removed'})
            
    return JsonResponse({'status': 'error', 'message': 'Error request'}, status=400)

@login_required
def diary_history_view(request):
    # 1. 获取前端传过来的日期参数 (例如: 2026-06-17)
    date_param = request.GET.get('date')
    
    # 如果没传日期，默认显示今天
    if not date_param:
        date_param = datetime.now().strftime('%Y-%m-%d')
        
    try:
        # 2. 转换日期格式用于前端抬头展示 (例如: "June 17, 2026")
        date_obj = datetime.strptime(date_param, '%Y-%m-%d')
        date_str = date_obj.strftime('%B %d, %Y')
    except ValueError:
        # 容错处理
        date_str = date_param

    # 3. 从数据库中查询该登录用户在这一天的所有日记
    # 这里的 user 和 date 字段请根据你具体的 Model 字段名进行调整
    # entries = DiaryEntry.objects.filter(user=request.user, date=date_param).order_by('created_at')
    entries = MoodEntry.objects.filter(user=request.user, entry_date=date_param ).order_by('created_at')

    context = {
        'entries': entries,
        'date_str': date_str,                 # 传给前端抬头显示，如 "June 10, 2026"
        'date_backend_str': date_param,       # 用于空状态下带去创建页，如 "2026-06-10"
    }
    
    return render(request, 'diaryhistory.html', context)

@login_required
def editentry_view(request):

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'delete':
            entry_id = request.POST.get('id')
            entry = MoodEntry.objects.filter(id=entry_id, user=request.user).first()
            if not entry:
                return JsonResponse({"status": "error", "message": "Entry not found."})
            entry.delete()
            return JsonResponse({"status": "success"})
                
        entry_id = request.POST.get('id')
        entry = MoodEntry.objects.filter(id=entry_id, user=request.user).first()
        if not entry:
            return JsonResponse({"status": "error", "message": "Entry not found."})
        entry.category = request.POST.get('category')
        entry.mood = request.POST.get('mood_name')
        entry.diary_text = request.POST.get('content')
        music_id = request.POST.get('music_id')
        
        if music_id:
            entry.selected_music = Music.objects.filter(id=music_id).first()
        deleted_photo_ids = json.loads(request.POST.get('deleted_photo_ids', '[]'))
        MoodPhoto.objects.filter(id__in=deleted_photo_ids, mood_entry=entry).delete()
        for photo in request.FILES.getlist('new_photos'):
            MoodPhoto.objects.create(mood_entry=entry, image=photo)
        entry.save()
        return JsonResponse({"status": "success"})
        
    entry_id = request.GET.get('id')

    entry = MoodEntry.objects.filter(
        id=entry_id,
        user=request.user
    ).first()

    if not entry:
        return redirect('diaryhistory')

    context = {
        'entry': entry,
        'songs': Music.objects.all(),
        'entry_date': entry.entry_date.strftime('%Y-%m-%d')
    }

    return render(request, 'editentry.html', context)

@csrf_exempt
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        try:
            user = request.user
            # 先注销用户的当前登录 session
            logout(request)
            # 从数据库中完全抹除用户记录
            user.delete()
            return JsonResponse({'status': 'success', 'message': 'Account deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

# 1. 渲染登录页
def admin_login_page_view(request):
    return render(request, 'login_admin.html')

# 2. 处理真实的登录逻辑
def admin_login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        # 使用 Django 自带的验证函数
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff: # 只有 staff 才能进后台
                login(request, user)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Not an admin'}, status=403)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'status': 'error'}, status=400)

# 3. 后台主页面
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin, login_url='/admin-login/')
def admin_portal_view(request):
    # 这里可以添加数据查询
    return render(request, 'admin.html')

# users/views.py

def article_admin_view(request):
    # 1. 从数据库查询所有文章
    articles = Article.objects.all()
    
    # 2. 将数据放在 context 字典中传给模板
    context = {
        'articles': articles
    }
    
    # 3. render 函数会自动处理这个 context
    return render(request, 'article_admin.html', context)

