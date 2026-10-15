from django.urls import path

from . import views

app_name = 'carrinho'

urlpatterns = [
    path('', views.index, name='index'),
    path('adicionar/<int:produto_id>/', views.adicionar, name='adicionar'),
    path('atualizar/<int:produto_id>/', views.atualizar, name='atualizar'),
    path('remover/<int:produto_id>/', views.remover, name='remover'),
    path('esvaziar/', views.esvaziar, name='esvaziar'),
]