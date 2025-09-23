from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    # Opciones para el tipo de pedido
    TIPO_PEDIDO_CHOICES = [
        ('recojo', 'Recojo en local'),
        ('delivery', 'Delivery'),
    ]
    
    # Campo tipo_pedido con las opciones
    tipo_pedido = forms.ChoiceField(
        choices=TIPO_PEDIDO_CHOICES,
        widget=forms.RadioSelect,
        label="¿Cómo deseas tu pedido?"
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'tipo_pedido', 'direccion', 'referencia']
        # Aquí es donde se añaden los widgets para los campos del formulario
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingresa tu nombre completo'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej. 912345678', 'type': 'tel'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej. Av. Los Girasoles 123'}),
            'referencia': forms.TextInput(attrs={'placeholder': 'Ej. Al lado de la tienda roja'}),
        }

    def clean_nombre(self):
        """
        Convierte el nombre a mayúsculas antes de guardarlo.
        """
        nombre = self.cleaned_data.get('nombre')
        return nombre.upper()

    def clean_telefono(self):
        """
        Valida que el teléfono tenga exactamente 9 dígitos.
        """
        telefono = self.cleaned_data.get('telefono')

        # Primero, asegúrate de que es un número
        if not telefono or not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener 9 dígitos.")

        # Luego, verifica la longitud
        if len(telefono) != 9:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 9 dígitos.")

        return telefono

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ocultar campos de dirección y referencia por defecto
        self.fields['direccion'].required = False
        self.fields['referencia'].required = False
        # Las clases CSS y placeholders ahora se manejan en el diccionario `widgets`
        # pero también se pueden sobreescribir aquí si es necesario.
        # Por ejemplo, para añadir clases a todos los campos:
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-input'})