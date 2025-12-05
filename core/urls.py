from django.urls import path
from . import views

urlpatterns = [
    # 1. Dashboard de Partidas
    # Rota principal para listar partidas salvas e iniciar uma nova.
    path('', views.dashboard, name='dashboard'), 

    # 2. Cadastro de Partidas
    # Rota para exibir o formulário e processar a criação de uma nova simulação
    path('nova/', views.nova_partida, name='nova_partida'), 

    # 3. Salvamento de Progresso
    # Rota que recebe os dados do jogo e salva no BDR (Salvamento de Progresso)
    # O <int:partida_id> é o ID da partida que o sistema deve atualizar.
    path('salvar/<int:partida_id>/', views.salvar_jogo, name='salvar_jogo'), 

    # 4. Continuidade de Partidas
    # Rota que busca os dados no BDR e restaura o estado do jogo (Carregamento
    path('carregar/<int:partida_id>/', views.carregar_jogo, name='carregar_jogo'),
]