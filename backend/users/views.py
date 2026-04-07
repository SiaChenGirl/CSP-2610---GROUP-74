from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'})

        User.objects.create_user(username=username, password=password)

        return JsonResponse({'message': 'User created successfully'})

    return JsonResponse({'error': 'Invalid request'})