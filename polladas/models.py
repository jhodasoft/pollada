from django.db import models

class ParteDelPollo(models.Model):
    nombre = models.CharField(max_length=50)
    # Por ejemplo: 'Pierna', 'Pecho', 'etc'
    cantidad_disponible = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=5, decimal_places=2, default=20.00) # <-- Agrega esta línea
    
    def __str__(self):
        return self.nombre

from django.db import models

class Cliente(models.Model):
    TIPO_PEDIDO_CHOICES = [
        ('recojo', 'Recojo en local'),
        ('delivery', 'Delivery'),
    ]

    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, unique=True)
    tipo_pedido = models.CharField(max_length=10, choices=TIPO_PEDIDO_CHOICES, default='recojo')
    direccion = models.CharField(max_length=255, blank=True, null=True)
    referencia = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Ticket(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    # Codigo unico del ticket (ej: "A1B2C3")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    parte_pollo = models.ForeignKey(ParteDelPollo, on_delete=models.CASCADE)
    pagado = models.BooleanField(default=False)
    canjeado = models.BooleanField(default=False)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket {self.codigo} - {self.cliente.nombre}"