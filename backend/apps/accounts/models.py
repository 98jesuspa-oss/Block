from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('vendor', 'Vendedor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='vendor')
    pin = models.CharField(max_length=4, blank=True, help_text='4-digit PIN for POS login')
    avatar_color = models.CharField(max_length=7, default='#04b906')

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [models.Index(fields=['username']), models.Index(fields=['role'])]

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def display_role(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if len(parts) >= 2:
            return parts[0][0].upper() + parts[1][0].upper()
        return self.username[:2].upper()

    def __str__(self):
        return self.get_full_name() or self.username
