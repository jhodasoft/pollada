# polladas/urls.py
from django.urls import path
from . import views

app_name = 'polladas' # <--- Asegúrate de que esta línea exista

urlpatterns = [
    path('', views.panel_principal, name='panel_principal'), # <-- Agrega esta línea
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('seleccionar-pollo/<int:cliente_id>/', views.seleccionar_pollo, name='seleccionar_pollo'),
    path('ticket/<str:codigo>/', views.mostrar_ticket, name='mostrar_ticket'), # <-- Agrega esta línea
    path('canjear/<str:codigo>/', views.canjear_ticket, name='canjear_ticket'), # <-- Agrega esta línea
    # path('canjear/', views.canjear_ticket, name='canjear_ticket'), # <-- Agrega esta línea
    path('buscar/', views.buscar_tickets_cliente, name='buscar_tickets_cliente'), # <-- Agrega esta línea
    path('reportes/', views.ver_reportes, name='ver_reportes'), # <-- Agrega esta línea
]