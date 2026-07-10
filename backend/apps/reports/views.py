from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from apps.sales.models import Sale, SaleItem


@login_required
def reports_view(request):
    periodo = request.GET.get('periodo', 'mes')
    today = timezone.localdate()

    if periodo == 'hoy':
        start, end = today, today
    elif periodo == 'semana':
        start = today - timedelta(days=today.weekday())
        end = today
    elif periodo == 'custom':
        try:
            from datetime import datetime
            start = datetime.strptime(request.GET.get('desde', str(today)), '%Y-%m-%d').date()
            end = datetime.strptime(request.GET.get('hasta', str(today)), '%Y-%m-%d').date()
        except ValueError:
            start, end = today.replace(day=1), today
    else:  # mes
        start = today.replace(day=1)
        end = today

    ventas = (Sale.objects.filter(fecha__gte=start, fecha__lte=end)
              .select_related('customer', 'user').order_by('-fecha', '-hora'))

    agg = ventas.aggregate(total=Sum('total'))
    total_ingresos = agg['total'] or 0
    total_ventas = ventas.count()
    ticket_promedio = (float(total_ingresos) / total_ventas) if total_ventas else 0

    total_piezas = (SaleItem.objects.filter(sale__fecha__gte=start, sale__fecha__lte=end)
                    .aggregate(t=Sum('cantidad'))['t'] or 0)

    top_items = (SaleItem.objects.filter(sale__fecha__gte=start, sale__fecha__lte=end)
                 .values('product__nombre')
                 .annotate(total_cant=Sum('cantidad'), total_importe=Sum('importe'))
                 .order_by('-total_importe')[:10])

    template = 'reports/partials/content.html' if request.headers.get('HX-Request') else 'reports/index.html'
    return render(request, template, {
        'ventas': ventas,
        'total_ingresos': total_ingresos,
        'total_ventas': total_ventas,
        'ticket_promedio': ticket_promedio,
        'total_piezas': total_piezas,
        'top_items': top_items,
        'periodo': periodo,
        'desde': start,
        'hasta': end,
    })


@login_required
def resumen_mensual(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    prev_end = month_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)

    ventas_mes = Sale.objects.filter(fecha__gte=month_start, fecha__lte=today)
    ventas_prev = Sale.objects.filter(fecha__gte=prev_start, fecha__lte=prev_end)
    total_mes = ventas_mes.aggregate(t=Sum('total'))['t'] or 0
    total_prev = ventas_prev.aggregate(t=Sum('total'))['t'] or 0
    delta_pct = ((float(total_mes) - float(total_prev)) / float(total_prev) * 100) if total_prev else 0
    total_ventas = ventas_mes.count()
    ticket_promedio = (float(total_mes) / total_ventas) if total_ventas else 0

    top_items = (SaleItem.objects.filter(sale__fecha__gte=month_start)
                 .values('product__nombre')
                 .annotate(total_cant=Sum('cantidad'), total_importe=Sum('importe'))
                 .order_by('-total_importe')[:10])

    MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
             'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    return render(request, 'reports/resumen.html', {
        'total_mes': total_mes,
        'total_ventas': total_ventas,
        'ticket_promedio': ticket_promedio,
        'delta_pct': delta_pct,
        'top_items': top_items,
        'mes_label': f'{MESES[today.month-1]} {today.year}',
        'now': timezone.localtime(),
        'empresa': __import__('django.conf', fromlist=['settings']).settings.VERDEBLOCK_EMPRESA,
    })