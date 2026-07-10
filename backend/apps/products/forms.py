import uuid
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    mayoreo = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'vb-input', 'step': '0.01'})
    )
    costo = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'vb-input', 'step': '0.01'})
    )

    class Meta:
        model = Product
        fields = ['sku', 'nombre', 'desc', 'categoria', 'unidad',
                  'precio', 'mayoreo', 'costo', 'stock', 'stock_min', 'activo']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'vb-input mono'}),
            'nombre': forms.TextInput(attrs={'class': 'vb-input'}),
            'desc': forms.Textarea(attrs={'class': 'vb-textarea', 'rows': 2}),
            'categoria': forms.Select(attrs={'class': 'vb-select'}),
            'unidad': forms.Select(attrs={'class': 'vb-select'}),
            'precio': forms.NumberInput(attrs={'class': 'vb-input', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'vb-input'}),
            'stock_min': forms.NumberInput(attrs={'class': 'vb-input'}),
        }

    def clean_sku(self):
        sku = self.cleaned_data.get('sku', '').strip()
        if not sku:
            sku = 'PROD-' + uuid.uuid4().hex[:6].upper()
        return sku

    def clean(self):
        cleaned = super().clean()
        precio = cleaned.get('precio') or 0
        if not cleaned.get('mayoreo'):
            cleaned['mayoreo'] = precio
        if cleaned.get('costo') is None:
            cleaned['costo'] = 0
        return cleaned