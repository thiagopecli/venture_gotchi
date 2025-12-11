from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [

    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'), 
    path('nova/', views.nova_partida, name='nova_partida'), 
    path('salvar/<int:partida_id>/', views.salvar_jogo, name='salvar_jogo'), 
    path('carregar/<int:partida_id>/', views.carregar_jogo, name='carregar_jogo'),
]