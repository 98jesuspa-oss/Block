from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from .models import Sale
from apps.products.models import Product
import locale


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    ventas_hoy_qs = Sale.objects.filter(fecha=today)
    ventas_hoy_total_raw = ventas_hoy_qs.aggregate(t=Sum('total'))['t'] or 0
    ventas_hoy_count = ventas_hoy_qs.count()

    ventas_mes_raw = Sale.objects.filter(fecha__gte=month_start).aggregate(t=Sum('total'))['t'] or 0

    productos = list(Product.objects.filter(activo=True))
    bajo_stock = [p for p in productos if p.bajo_stock]

    ultimas_ventas = Sale.objects.select_related('customer', 'user').order_by('-fecha', '-hora')[:8]

    MESES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']
    DIAS = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    dow = DIAS[today.weekday()]
    mes = MESES[today.month - 1]
    today_label = f'Hoy es {dow} {today.day} de {mes}, {today.year}'
    mes_label = f'{mes.capitalize()} {today.year}'

    return render(request, 'dashboard/index.html', {
        'ventas_hoy_total': f'${ventas_hoy_total_raw:,.2f}',
        'ventas_hoy_total_raw': float(ventas_hoy_total_raw),
        'ventas_hoy_count': ventas_hoy_count,
        'ventas_mes_total': f'${ventas_mes_raw:,.2f}',
        'ventas_mes_total_raw': float(ventas_mes_raw),
        'bajo_stock_count': len(bajo_stock),
        'bajo_stock': bajo_stock[:8],
        'ultimas_ventas': ultimas_ventas,
        'today_label': today_label,
        'mes_label': mes_label,
    })