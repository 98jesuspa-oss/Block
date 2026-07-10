from django.db import models
from django.conf import settings

METODO_CHOICES = [
    ('efectivo','Efectivo'),('transferencia','Transferencia'),
    ('tarjeta','Tarjeta'),('credito','Credito'),
]

class Sale(models.Model):
    folio = models.CharField(max_length=20, unique=True, db_index=True)
    fecha = models.DateField(db_index=True)
    hora = models.TimeField()
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT,
        related_name='sales', null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='sales'
    )
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES, default='efectivo')
    aplica_iva = models.BooleanField(default=False)
    descuento_pct = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    iva_monto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_sale'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha', '-hora']
        indexes = [
            models.Index(fields=['-fecha', '-hora']),
            models.Index(fields=['customer', '-fecha']),
            models.Index(fields=['user', '-fecha']),
        ]

    def recalculate(self):
        sub = sum(float(i.importe) for i in self.items.all())
        desc = sub * float(self.descuento_pct)
        base = sub - desc
        iva = base * 0.16 if self.aplica_iva else 0
        self.subtotal = sub
        self.descuento_monto = desc
        self.iva_monto = iva
        self.total = base + iva

    def __str__(self):
        return self.folio


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT, related_name='sale_items'
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    importe = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = 'sales_saleitem'
        indexes = [models.Index(fields=['sale']), models.Index(fields=['product'])]

    def save(self, *args, **kwargs):
        self.importe = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} x{self.cantidad}'