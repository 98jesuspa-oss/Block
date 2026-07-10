import json
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.paginator import Paginator
from .models import Product, InventoryMovement, CATEGORY_CHOICES, UNIT_CHOICES
from .forms import ProductForm


@login_required
def products_list(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '')
    qs = Product.objects.filter(activo=True).order_by('categoria', 'nombre')
    if q:
        qs = qs.filter(nombre__icontains=q) | Product.objects.filter(sku__icontains=q, activo=True)
        qs = qs.distinct().order_by('categoria', 'nombre')
    if cat:
        qs = qs.filter(categoria=cat)
    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(request.GET.get('page'))
    bajos_count = Product.objects.filter(activo=True).count()  # rough; refined below
    all_active = list(Product.objects.filter(activo=True))
    bajos_count = sum(1 for p in all_active if p.bajo_stock)
    ctx = {
        'productos': page_obj.object_list,
        'page_obj': page_obj,
        'categorias': CATEGORY_CHOICES,
        'bajos_count': bajos_count,
        'q': q,
        'cat': cat,
    }
    if request.htmx:
        return render(request, 'products/partials/table.html', ctx)
    return render(request, 'products/index.html', ctx)


@login_required
def product_table(request):
    return products_list(request)


@login_required
def product_pos_search(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '')
    qs = Product.objects.filter(activo=True).order_by('categoria', 'nombre')
    if q:
        qs = qs.filter(nombre__icontains=q)
    if cat:
        qs = qs.filter(categoria=cat)
    return render(request, 'sales/partials/pos_products.html', {'productos': list(qs[:60])})


@login_required
def product_movements_json(request, pk):
    p = get_object_or_404(Product, pk=pk)
    movs = list(p.movements.order_by('-created_at')[:20].values(
        'id','tipo','cantidad','stock_after','nota','created_at'))
    for m in movs:
        m['created_at'] = m['created_at'].strftime('%Y-%m-%d %H:%M') if m['created_at'] else ''
    return JsonResponse(movs, safe=False)


@login_required
@require_POST
def product_movement(request, pk):
    p = get_object_or_404(Product, pk=pk)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    tipo = data.get('tipo', 'entrada')
    cant = int(data.get('cantidad', 0))
    nota = data.get('nota', '')
    if cant <= 0:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)
    with transaction.atomic():
        delta = cant if tipo == 'entrada' else -cant
        p.stock = max(0, p.stock + delta)
        p.save(update_fields=['stock'])
        mov = InventoryMovement.objects.create(
            product=p, tipo=tipo, cantidad=delta,
            stock_after=p.stock, nota=nota, user=request.user,
        )
    return JsonResponse({'ok': True, 'stock': p.stock, 'mov': {
        'id': mov.id, 'tipo': mov.tipo, 'cantidad': mov.cantidad,
        'stock_after': mov.stock_after, 'nota': mov.nota,
        'created_at': mov.created_at.strftime('%Y-%m-%d %H:%M'),
    }})


@login_required
def product_form(request, pk=None):
    obj = get_object_or_404(Product, pk=pk) if pk else None
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            all_active = list(Product.objects.filter(activo=True))
            bajos_count = sum(1 for p in all_active if p.bajo_stock)
            qs = Product.objects.filter(activo=True).order_by('categoria', 'nombre')
            paginator = Paginator(qs, 40)
            page_obj = paginator.get_page(1)
            resp = render(request, 'products/partials/table.html', {
                'productos': page_obj.object_list,
                'page_obj': page_obj,
                'categorias': CATEGORY_CHOICES,
                'bajos_count': bajos_count,
            })
            resp['X-Toast'] = urllib.parse.quote('Producto guardado')
            return resp
        ctx = {
            'producto': obj or Product(),
            'categorias': CATEGORY_CHOICES,
            'unidades': UNIT_CHOICES,
            'form_errors': form.errors,
        }
        resp = render(request, 'products/partials/form.html', ctx)
        resp.status_code = 422
        resp['HX-Retarget'] = '#modal-container'
        resp['HX-Reswap'] = 'innerHTML'
        return resp
    ctx = {
        'producto': obj or Product(),
        'categorias': CATEGORY_CHOICES,
        'unidades': UNIT_CHOICES,
    }
    return render(request, 'products/partials/form.html', ctx)


@login_required
@require_POST
def product_delete(request, pk):
    p = get_object_or_404(Product, pk=pk)
    p.activo = False
    p.save(update_fields=['activo'])
    qs = Product.objects.filter(activo=True).order_by('categoria', 'nombre')
    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(1)
    all_active = list(qs)
    bajos_count = sum(1 for pr in all_active if pr.bajo_stock)
    resp = render(request, 'products/partials/table.html', {
        'productos': page_obj.object_list,
        'page_obj': page_obj,
        'categorias': CATEGORY_CHOICES,
        'bajos_count': bajos_count,
    })
    resp['X-Toast'] = urllib.parse.quote('Producto desactivado')
    return resp