# polladas/views.py

from django.shortcuts import render, redirect, get_object_or_404
import uuid
from django.contrib.auth.decorators import login_required 
from django.urls import reverse
from django.db import transaction
from django.db.models import Count, Q, Sum

from .models import Cliente, ParteDelPollo, Ticket
from .forms import ClienteForm

import qrcode
import base64
from io import BytesIO

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            telefono = form.cleaned_data['telefono']
            tipo_pedido = form.cleaned_data['tipo_pedido']
            
            direccion = form.cleaned_data.get('direccion')
            referencia = form.cleaned_data.get('referencia')

            cliente, created = Cliente.objects.get_or_create(
                telefono=telefono,
                defaults={
                    'nombre': nombre,
                    'tipo_pedido': tipo_pedido,
                    'direccion': direccion,
                    'referencia': referencia
                }
            )

            if not created:
                cliente.nombre = nombre
                cliente.tipo_pedido = tipo_pedido
                cliente.direccion = direccion
                cliente.referencia = referencia
                cliente.save()

            return redirect('polladas:seleccionar_pollo', cliente_id=cliente.id)
    else:
        form = ClienteForm()

    return render(request, 'polladas/registrar_cliente.html', {'form': form})

def seleccionar_pollo(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    partes_disponibles = ParteDelPollo.objects.filter(cantidad_disponible__gt=0)

    if request.method == 'POST':
        parte_pollo_id = request.POST.get('parte_pollo')
        parte_pollo = get_object_or_404(ParteDelPollo, pk=parte_pollo_id)

        codigo = str(uuid.uuid4())[:8].upper()

        if parte_pollo.cantidad_disponible > 0:
            ticket = Ticket.objects.create(
                cliente=cliente,
                parte_pollo=parte_pollo,
                codigo=codigo
            )

            parte_pollo.cantidad_disponible -= 1
            parte_pollo.save()

            return redirect('polladas:mostrar_ticket', codigo=ticket.codigo)

    context = {
        'cliente': cliente,
        'partes_disponibles': partes_disponibles
    }
    return render(request, 'polladas/seleccionar_pollo.html', context)

def mostrar_ticket(request, codigo):
    try:
        ticket = get_object_or_404(Ticket, codigo=codigo)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_url = request.build_absolute_uri(reverse('polladas:mostrar_ticket', kwargs={'codigo': ticket.codigo}))
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        contexto = {
            'ticket': ticket,
            'qr_data': qr_data
        }
    
    except Ticket.DoesNotExist:
        return redirect('polladas:registrar_cliente') 
    
    return render(request, 'polladas/mostrar_ticket.html', contexto)

@login_required 
def canjear_ticket(request, codigo):
    context = {}
    
    # Intenta obtener el código del formulario POST o del parámetro GET en la URL
    codigo_ingresado = codigo or request.POST.get('codigo_ticket') or request.GET.get('codigo')

    if codigo_ingresado:
        try:
            with transaction.atomic():
                ticket = Ticket.objects.select_for_update().get(codigo=codigo_ingresado.upper())
                if not ticket.pagado:
                    mensaje = "Error: Este ticket no ha sido pagado."
                    color = "rojo"
                elif ticket.canjeado:
                    mensaje = "Error: Este ticket ya ha sido canjeado."
                    color = "rojo"
                else:
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
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) | Q(telefono__icontains=query)
        ).distinct()
        
        for cliente in clientes:
            tickets.extend(cliente.ticket_set.all())

    context = {
        'tickets': tickets,
        'query': query,
    }
    return render(request, 'polladas/buscar_tickets_cliente.html', context)

def ver_reportes(request):
    dinero_recaudado = Ticket.objects.filter(pagado=True).aggregate(
        total=Sum('parte_pollo__precio')
    )['total'] or 0

    dinero_pendiente = Ticket.objects.filter(pagado=False).aggregate(
        total=Sum('parte_pollo__precio')
    )['total'] or 0

    tickets_vendidos = Ticket.objects.filter(pagado=True).count()

    tickets_canjeados = Ticket.objects.filter(canjeado=True).count()

    pedidos_delivery = Ticket.objects.filter(cliente__tipo_pedido='delivery',pagado=True).count()

    delivery_pendientes = Ticket.objects.filter(
        cliente__tipo_pedido='delivery',
        canjeado=False,
        pagado=True
    ).select_related('cliente', 'parte_pollo').order_by('cliente__nombre')

    ventas_por_parte = ParteDelPollo.objects.annotate(
        total_vendido=Count('ticket')
    ).order_by('nombre')

    tickets_no_pagados = Ticket.objects.filter(pagado=False).select_related('cliente', 'parte_pollo')

    partes_populares = ParteDelPollo.objects.annotate(
        total_vendido=Count('ticket')
    ).order_by('-total_vendido')[:3]

    context = {
        'dinero_recaudado': dinero_recaudado,
        'dinero_pendiente': dinero_pendiente,
        'tickets_vendidos': tickets_vendidos,
        'tickets_canjeados': tickets_canjeados,
        'pedidos_delivery': pedidos_delivery,
        'delivery_pendientes': delivery_pendientes,
        'ventas_por_parte': ventas_por_parte,
        'tickets_no_pagados': tickets_no_pagados,
        'partes_populares': partes_populares
    }
    return render(request, 'polladas/reportes.html', context)

def panel_principal(request):
    return render(request, 'polladas/panel_principal.html')