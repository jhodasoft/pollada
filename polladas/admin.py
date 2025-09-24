# polladas/admin.py
from django.contrib import admin
from .models import Cliente, ParteDelPollo, Ticket

# Filtro para ver solo los tickets pagados o no pagados
class TicketPagadoFilter(admin.SimpleListFilter):
    title = 'Estado de Pago'
    parameter_name = 'pagado_status'

    def lookups(self, request, model_admin):
        return [
            ('pagados', 'Pagados'),
            ('no_pagados', 'No Pagados'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'pagados':
            return queryset.filter(pagado=True)
        if self.value() == 'no_pagados':
            return queryset.filter(pagado=False)
        return queryset

# Acción para marcar tickets como pagados
@admin.action(description='Marcar tickets seleccionados como pagados')
def marcar_como_pagado(modeladmin, request, queryset):
    queryset.update(pagado=True)

class TicketAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'parte_pollo', 'pagado', 'canjeado', 'fecha_venta')
    list_filter = (TicketPagadoFilter, 'canjeado')
    search_fields = ('codigo', 'cliente__nombre', 'cliente__telefono')
    actions = [marcar_como_pagado]
    readonly_fields = ('codigo',) # Para que el código del ticket no se pueda editar manualmente

class ParteDelPolloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_disponible','precio')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'tipo_pedido', 'direccion', 'referencia')

admin.site.register(Cliente,ClienteAdmin)
admin.site.register(ParteDelPollo, ParteDelPolloAdmin)
admin.site.register(Ticket, TicketAdmin)