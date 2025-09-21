# polladas/forms.py
from django import forms

class ClienteForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    telefono = forms.CharField(max_length=20)