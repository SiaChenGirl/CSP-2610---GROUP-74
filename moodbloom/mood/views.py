import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Mood, Article, Feedback
from django.contrib.auth.models import User
from django.db.models import Count, Avg, DateField
from django.db.models.functions import Cast

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
    return render(request, 'profile.html', {'profile': profile})

def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(request, username=data.get('username'), password=data.get('password'))
        if user:
            login(request, user)
            return JsonResponse({'message': 'OK'})
        return JsonResponse({'error': 'Invalid'}, status=400)
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def register_view(request): 
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.create_user(username=data.get('username'), password=data.get('password'), email=data.get('email'))
        Profile.objects.create(user=user, gender=data.get('gender', 'Others'))
        return JsonResponse({'message': 'OK'})
    return render(request, 'register.html')

@login_required
def mainpage_view(request): return render(request, 'mainpage.html')

@login_required
def moodentry_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Mood.objects.create(user=request.user, category=data.get('category'), mood_name=data.get('mood_name'), intensity=data.get('intensity'), content=data.get('content'), song=data.get('song'))
        return JsonResponse({'status': 'success'})
    return render(request, 'moodentry.html')

@login_required
def dashboard_view(request): 
    user_moods = Mood.objects.filter(user=request.user)
    distribution = list(user_moods.values('category').annotate(count=Count('id')))
    trends_query = user_moods.annotate(date_only=Cast('created_at', DateField())).values('date_only').annotate(avg_intensity=Avg('intensity')).order_by('date_only')
    trends_list = [{'created_at__date': str(i['date_only']), 'avg_intensity': float(i['avg_intensity'])} for i in trends_query]
    return render(request, 'dashboard.html', {'moods': user_moods.order_by('-created_at'), 'mood_distribution_json': json.dumps(distribution), 'mood_trends_json': json.dumps(trends_list)})

# 文章页面显示
@login_required
def article_view(request):
    return render(request, 'article.html')

# API：根据分类获取文章链接
@login_required
def get_articles_by_category(request):
    cat = request.GET.get('category')
    articles = Article.objects.filter(category=cat).values('title', 'summary', 'external_url')
    return JsonResponse(list(articles), safe=False)

@login_required
def feedback_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Feedback.objects.create(user=request.user, subject=data.get('subject'), rating=data.get('rating'), content=data.get('content'))
        return JsonResponse({'status': 'success'})
    return render(request, 'feedback.html')

@login_required
def gallery_view(request): return render(request, 'gallery.html', {'moods': Mood.objects.filter(user=request.user)})
@login_required
def search_view(request): return render(request, 'search.html')
def forgot_view(request): return render(request, 'forgot.html')