import urllib.parse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm


@login_required
def customers_list(request):
    q = request.GET.get('q', '').strip()
    qs = Customer.objects.filter(activo=True).order_by('nombre')
    if q:
        qs = qs.filter(nombre__icontains=q)
    clientes = list(qs.annotate_ventas() if hasattr(qs, 'annotate_ventas') else qs)
    if request.htmx:
        return render(request, 'customers/partials/table.html', {'clientes': clientes})
    return render(request, 'customers/index.html', {'clientes': clientes, 'q': q})


@login_required
def customer_table(request):
    return customers_list(request)


@login_required
def customer_search(request):
    """Used by POS paso-1 HTMX search"""
    q = request.GET.get('q', '').strip()
    qs = Customer.objects.filter(activo=True).order_by('nombre')
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(nombre__icontains=q) | Q(tel__icontains=q))
    clientes = list(qs[:20])
    return render(request, 'sales/partials/clientes_lista.html', {'clientes': clientes})


@login_required
def customer_form(request, pk=None):
    obj = get_object_or_404(Customer, pk=pk) if pk else None
    is_htmx = bool(request.headers.get('HX-Request'))
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            if is_htmx:
                qs = Customer.objects.filter(activo=True).order_by('nombre')
                resp = render(request, 'customers/partials/table.html', {'clientes': list(qs)})
                resp['X-Toast'] = urllib.parse.quote('Cliente guardado')
                resp['HX-Trigger'] = 'customers:reload'
                return resp
            return redirect('customers:index')
    ctx = {'cliente': obj or Customer()}
    template = 'customers/partials/form.html' if is_htmx else 'customers/form_page.html'
    return render(request, template, ctx)


@login_required
def customer_update(request, pk):
    return customer_form(request, pk=pk)


@login_required
def customer_create(request):
    return customer_form(request)