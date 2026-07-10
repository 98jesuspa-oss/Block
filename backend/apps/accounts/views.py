import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    users = User.objects.filter(is_active=True).values('id', 'first_name', 'last_name', 'username', 'role')
    users_list = [
        {
            'id': u['id'],
            'name': f"{u['first_name']} {u['last_name']}".strip() or u['username'],
            'role': dict(User.ROLE_CHOICES).get(u['role'], u['role']),
        }
        for u in users
    ]
    return render(request, 'accounts/login.html', {'users_json': json.dumps(users_list)})


@require_POST
def verify_pin(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    user_id = data.get('user_id')
    pin = data.get('pin', '')

    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'ok': False})

    if user.pin and user.pin == pin:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return JsonResponse({'ok': True, 'redirect': '/'})
    return JsonResponse({'ok': False})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
