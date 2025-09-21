# polladas/views.py

# Asegúrate de que los imports de arriba incluyan estos
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.db.models import Count, Q, Sum
# Y tus modelos
from .models import Cliente, ParteDelPollo, Ticket
from .forms import ClienteForm
# Importamos la librería para generar QR
import qrcode
import base64
from io import BytesIO

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            telefono = form.cleaned_data['telefono']

            # Intentar obtener el cliente existente o crearlo si no existe
            cliente, created = Cliente.objects.get_or_create(
                telefono=telefono,
                defaults={'nombre': nombre}
            )
            
            # Si el cliente ya existía, pero el nombre es diferente, se puede actualizar
            if not created and cliente.nombre != nombre:
                cliente.nombre = nombre
                cliente.save()

            return redirect('seleccionar_pollo', cliente_id=cliente.id)
    else:
        form = ClienteForm()

    return render(request, 'polladas/registrar_cliente.html', {'form': form})

def seleccionar_pollo(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    partes_disponibles = ParteDelPollo.objects.filter(cantidad_disponible__gt=0)

    if request.method == 'POST':
        parte_pollo_id = request.POST.get('parte_pollo')
        parte_pollo = get_object_or_404(ParteDelPollo, pk=parte_pollo_id)

        # Crear un código de ticket simple. En un sistema real se haría más robusto.
        import uuid
        codigo = str(uuid.uuid4())[:8].upper()

        if parte_pollo.cantidad_disponible > 0:
            # Crear el ticket
            Ticket.objects.create(
                cliente=cliente,
                parte_pollo=parte_pollo,
                codigo=codigo
            )

            # Descontar la cantidad disponible
            parte_pollo.cantidad_disponible -= 1
            parte_pollo.save()

            return redirect('mostrar_ticket', codigo=codigo)

    context = {
        'cliente': cliente,
        'partes_disponibles': partes_disponibles
    }
    return render(request, 'polladas/seleccionar_pollo.html', context)

def mostrar_ticket(request, codigo):
    try:
        ticket = get_object_or_404(Ticket, codigo=codigo)

        # Creamos la URL de canje completa para el QR
        canje_url = request.build_absolute_uri(reverse('canjear_ticket')) + f'?codigo={ticket.codigo}'

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(canje_url) # <-- El QR ahora contiene la URL de canje
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convertimos la imagen del QR a una cadena de texto para la plantilla
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        context = {
            'ticket': ticket,
            'qr_data': qr_data,
        }
        return render(request, 'polladas/mostrar_ticket.html', context)

    except Exception as e:
        # Añadir un manejo de errores básico para ver qué está pasando
        print(f"Error en mostrar_ticket: {e}")
        return redirect('registrar_cliente')

def canjear_ticket(request):
    context = {}
    
    # Intenta obtener el código del formulario POST o del parámetro GET en la URL
    codigo_ingresado = request.POST.get('codigo_ticket') or request.GET.get('codigo')

    if codigo_ingresado:
        try:
            with transaction.atomic():
                ticket = Ticket.objects.select_for_update().get(codigo=codigo_ingresado.upper()) # Convierte a mayúsculas
                if not ticket.pagado:
                    mensaje = "Error: Este ticket no ha sido pagado."
                    color = "rojo"
                elif ticket.canjeado:
                    mensaje = "Error: Este ticket ya ha sido canjeado."
                    color = "rojo"
                else:
                    # Marcar el ticket como canjeado
                    ticket.canjeado = True
                    ticket.save()
                    mensaje = f"Éxito: Ticket {ticket.codigo} canjeado. ¡Disfruta de tu {ticket.parte_pollo.nombre}!"
                    color = "verde"
                    context['ticket_canjeado'] = ticket
        except Ticket.DoesNotExist:
            mensaje = "Error: Código de ticket no válido."
            color = "rojo"
        
        context['mensaje'] = mensaje
        context['color'] = color

    return render(request, 'polladas/canjear_ticket.html', context)

def buscar_tickets_cliente(request):
    query = request.GET.get('q')
    tickets = []
    
    if query:
        # Buscar clientes que coincidan con el nombre o teléfono
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(telefono__icontains=query)
        ).distinct()
        
        # Obtener todos los tickets de los clientes encontrados
        for cliente in clientes:
            tickets.extend(cliente.ticket_set.all())

    context = {
        'tickets': tickets,
        'query': query,
    }
    return render(request, 'polladas/buscar_tickets_cliente.html', context)

def ver_reportes(request):
    # Obtener el total de tickets vendidos (pagados)
    tickets_vendidos = Ticket.objects.filter(pagado=True).count()

    # Obtener el total de tickets canjeados
    tickets_canjeados = Ticket.objects.filter(canjeado=True).count()

    # Calcular el dinero recaudado de los tickets pagados
    dinero_recaudado = Ticket.objects.filter(pagado=True).aggregate(
        total=Sum('parte_pollo__precio')
    )['total'] or 0

    # Obtener la lista de tickets no pagados
    tickets_no_pagados = Ticket.objects.filter(pagado=False).order_by('cliente__nombre')

    # Calcular el dinero pendiente de cobro
    dinero_pendiente = Ticket.objects.filter(pagado=False).aggregate(
        total=Sum('parte_pollo__precio')
    )['total'] or 0

    # Obtener las ventas por cada parte del pollo
    ventas_por_parte = ParteDelPollo.objects.annotate(
        total_vendido=Count('ticket', filter=Q(ticket__pagado=True))
    ).order_by('-total_vendido')

    # Obtener las partes más populares
    partes_populares = ParteDelPollo.objects.annotate(
        total_vendido=Count('ticket', filter=Q(ticket__pagado=True))
    ).order_by('-total_vendido')[:3]

    context = {
        'tickets_vendidos': tickets_vendidos,
        'tickets_canjeados': tickets_canjeados,
        'dinero_recaudado': dinero_recaudado, # <-- Agrega esta línea
        'dinero_pendiente': dinero_pendiente, # <-- Agrega esta línea
        'tickets_no_pagados': tickets_no_pagados,
        'ventas_por_parte': ventas_por_parte,
        'partes_populares': partes_populares,
    }
    return render(request, 'polladas/reportes.html', context)

def panel_principal(request):
    return render(request, 'polladas/panel_principal.html')