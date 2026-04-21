from django.shortcuts import render
from django.http import HttpResponse

# 这些是占位函数，保证项目能跑起来
def login_view(request):
    # 这里要填入你队友写的 HTML 文件名，通常是 'login.html'
    return render(request, 'index.html')

def register(request):
    return HttpResponse("Register Page")

def dashboard(request):
    return HttpResponse("Dashboard Page")