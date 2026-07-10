from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [
    ('block', 'Block'),
    ('cemento', 'Cemento y Cal'),
    ('acero', 'Acero'),
    ('agregados', 'Agregados'),
    ('prefabricados', 'Prefabricados'),
    ('otros', 'Otros'),
]
UNIT_CHOICES = [
    ('pieza','Pieza'),('saco','Saco'),('m3','Metro cubico'),
    ('kg','Kilogramo'),('hoja','Hoja'),('millar','Millar'),
    ('m2','Metro cuadrado'),('cubeta','Cubeta'),
]
MOV_TYPES = [
    ('entrada','Entrada'),('salida','Salida'),('ajuste','Ajuste'),('venta','Venta'),
]


class Product(models.Model):
    sku = models.CharField(max_length=40, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    categoria = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='otros', db_index=True)
    unidad = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieza')
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    mayoreo = models.DecimalField(max_digits=12, decimal_places=2)
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_min = models.IntegerField(default=0)
    activo = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products_product'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['categoria', 'nombre']
        indexes = [
            models.Index(fields=['activo', 'categoria']),
            models.Index(fields=['stock', 'stock_min']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(precio__gte=0), name='precio_gte_0'),
            models.CheckConstraint(check=models.Q(stock__gte=0), name='stock_gte_0'),
        ]

    @property
    def bajo_stock(self):
        return self.activo and self.stock <= self.stock_min

    @property
    def stock_tone(self):
        if self.stock <= 0: return 'danger'
        if self.stock <= self.stock_min: return 'danger'
        if self.stock <= self.stock_min * 1.5: return 'warn'
        return 'ok'

    @property
    def margen(self):
        if self.costo and self.precio:
            return round((float(self.precio) - float(self.costo)) / float(self.precio) * 100, 1)
        return 0

    @property
    def categoria_label(self):
        return dict(CATEGORY_CHOICES).get(self.categoria, self.categoria)

    def __str__(self):
        return self.nombre


class InventoryMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='movements')
    tipo = models.CharField(max_length=20, choices=MOV_TYPES)
    cantidad = models.IntegerField()
    stock_after = models.IntegerField()
    nota = models.CharField(max_length=300, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='inventory_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products_movement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} {self.cantidad} x {self.product}'