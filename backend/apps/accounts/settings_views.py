from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import User
import urllib.parse

FONT_SCALES = [('normal', 'Normal'), ('grande', 'Grande'), ('xl', 'XL')]


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
def settings_view(request):
    usuarios = User.objects.filter(is_active=True).order_by('first_name')
    empresa = settings.VERDEBLOCK_EMPRESA
    return render(request, 'settings/index.html', {
        'usuarios': usuarios,
        'empresa': empresa,
        'font_scales': FONT_SCALES,
    })


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.role = request.POST.get('role', user.role)
        pin = request.POST.get('pin', '').strip()
        if pin and len(pin) == 4 and pin.isdigit():
            user.pin = pin
        user.save()
        response = HttpResponse(status=204)
        response['X-Toast'] = urllib.parse.quote(f'Usuario actualizado')
        return response
    return render(request, 'settings/partials/user_form.html', {'usuario': user})


@login_required
@user_passes_test(is_admin)
def company_save(request):
    if request.method == 'POST':
        response = HttpResponse(status=204)
        response['X-Toast'] = urllib.parse.quote('Datos de empresa guardados')
        return response
    return HttpResponse(status=405)


@login_required
@user_passes_test(is_admin)
def user_form(request, pk=None):
    obj = get_object_or_404(User, pk=pk) if pk else None
    if request.method == 'POST':
        if obj:
            obj.first_name = request.POST.get('first_name', obj.first_name)
            obj.last_name = request.POST.get('last_name', obj.last_name)
            obj.role = request.POST.get('role', obj.role)
            pin = request.POST.get('pin', '').strip()
            if pin and len(pin) == 4 and pin.isdigit():
                obj.pin = pin
            obj.save()
        else:
            import secrets
            new_user = User(
                username=request.POST.get('username', f'user_{secrets.token_hex(3)}'),
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                role=request.POST.get('role', 'vendor'),
            )
            new_user.set_unusable_password()
            pin = request.POST.get('pin', '').strip()
            if pin and len(pin) == 4 and pin.isdigit():
                new_user.pin = pin
            new_user.save()
        usuarios = User.objects.filter(is_active=True).order_by('first_name')
        resp = HttpResponse(status=204)
        resp['X-Toast'] = urllib.parse.quote('Usuario guardado')
        resp['HX-Trigger'] = 'users:reload'
        return resp
    return render(request, 'settings/partials/user_form.html', {'usuario': obj or User()})