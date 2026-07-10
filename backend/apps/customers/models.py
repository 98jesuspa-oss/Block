from django.db import models

TIPO_CHOICES = [('publico','Publico'),('mayoreo','Mayoreo')]

class Customer(models.Model):
    nombre = models.CharField(max_length=200, db_index=True)
    contacto = models.CharField(max_length=200, blank=True)
    tel = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    dir = models.CharField(max_length=300, blank=True)
    rfc = models.CharField(max_length=20, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='publico', db_index=True)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers_customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['tipo','activo']),
            models.Index(fields=['nombre']),
        ]

    @property
    def tipo_label(self):
        return 'Mayoreo' if self.tipo == 'mayoreo' else 'Publico'

    @property
    def initials(self):
        parts = self.nombre.split()
        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()
        return self.nombre[:2].upper()

    def __str__(self):
        return self.nombre