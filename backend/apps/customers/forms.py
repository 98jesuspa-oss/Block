from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['nombre','contacto','tel','email','dir','rfc','tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'vb-input','autofocus':True}),
            'contacto': forms.TextInput(attrs={'class':'vb-input'}),
            'tel': forms.TextInput(attrs={'class':'vb-input'}),
            'email': forms.EmailInput(attrs={'class':'vb-input'}),
            'dir': forms.TextInput(attrs={'class':'vb-input'}),
            'rfc': forms.TextInput(attrs={'class':'vb-input mono'}),
            'tipo': forms.Select(attrs={'class':'vb-select'}),
        }