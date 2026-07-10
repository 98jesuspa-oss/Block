import json
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from .models import Sale, SaleItem
from apps.products.models import Product, InventoryMovement, CATEGORY_CHOICES
from apps.customers.models import Customer


@login_required
def pos_view(request):
    productos = Product.objects.filter(activo=True).order_by('categoria', 'nombre')
    clientes = Customer.objects.filter(activo=True).order_by('nombre')
    return render(request, 'sales/pos.html', {
        'productos': productos,
        'clientes': clientes,
        'categorias': CATEGORY_CHOICES,
        'metodos_pago': ['Efectivo', 'Transferencia', 'Tarjeta', 'Cheque'],
    })


@login_required
@require_POST
def create_sale(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    cliente_id = data.get('cliente_id')
    metodo = data.get('metodo', 'Efectivo')
    aplica_iva = bool(data.get('iva', False))
    desc_pct = float(data.get('desc_pct', 0))
    items_data = data.get('items', [])

    if not items_data:
        return JsonResponse({'ok': False, 'error': 'No items'}, status=400)

    with transaction.atomic():
        last = Sale.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1001
        folio = f'VB-{num:04d}'
        now = timezone.localtime()

        customer_id = cliente_id if cliente_id and cliente_id != 0 else None
        sale = Sale.objects.create(
            folio=folio, fecha=now.date(), hora=now.time(),
            customer_id=customer_id, user=request.user,
            metodo=metodo, aplica_iva=aplica_iva, descuento_pct=desc_pct,
        )

        for item in items_data:
            prod = get_object_or_404(Product, pk=item['product_id'])
            cant = int(item['cant'])
            precio = float(item['precio'])
            SaleItem.objects.create(
                sale=sale, product=prod,
                cantidad=cant, precio_unitario=precio,
            )
            prod.stock = max(0, prod.stock - cant)
            prod.save(update_fields=['stock'])
            InventoryMovement.objects.create(
                product=prod, tipo='venta', cantidad=-cant,
                stock_after=prod.stock, nota=f'Venta {folio}', user=request.user,
            )

        sale.recalculate()
        sale.save(update_fields=['subtotal', 'descuento_monto', 'iva_monto', 'total'])

    return JsonResponse({'ok': True, 'folio': folio, 'total': float(sale.total)})


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'user').prefetch_related('items__product'),
        pk=pk
    )
    from django.conf import settings
    empresa = settings.VERDEBLOCK_EMPRESA
    return render(request, 'sales/nota.html', {'venta': sale, 'empresa': empresa})


@login_required
def sale_nota_by_pk(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'user').prefetch_related('items__product'),
        pk=pk
    )
    from django.conf import settings
    empresa = settings.VERDEBLOCK_EMPRESA
    return render(request, 'sales/nota.html', {'venta': sale, 'empresa': empresa})


@login_required
def sale_nota(request, folio):
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'user').prefetch_related('items__product'),
        folio=folio
    )
    from django.conf import settings
    empresa = settings.VERDEBLOCK_EMPRESA
    return render(request, 'sales/nota.html', {'venta': sale, 'empresa': empresa})