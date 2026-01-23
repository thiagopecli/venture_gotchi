from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [

    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('redirect/', views.redirect_handler, name='redirect_handler'),
    path('', views.dashboard, name='dashboard'), 
    path('nova/', views.nova_partida, name='nova_partida'), 
    path('salvar/<int:partida_id>/', views.salvar_jogo, name='salvar_jogo'), 
    path('carregar/<int:partida_id>/', views.carregar_jogo, name='carregar_jogo'),
    path('perfil/', views.perfil, name='perfil'),
    path('historico/', views.historico, name='historico'),
    path('metricas/<int:partida_id>/', views.metricas, name='metricas'),
    path('conquistas/', views.conquistas, name='conquistas'),
    path('ranking/', views.ranking, name='ranking'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('educador/', views.educador_dashboard, name='educador_dashboard'),
    path('educador/perfil/', views.educador_perfil, name='educador_perfil'),
    path('educador/perfil/editar/', views.educador_editar_perfil, name='educador_editar_perfil'),
    path('criar-turma/', views.criar_turma, name='criar_turma'),
    path('turma/<str:codigo_turma>/', views.analise_turma, name='analise_turma'),
    path('ranking-turmas/', views.ranking_turmas, name='ranking_turmas'),
    path('metricas-turmas/', views.metricas_turmas, name='metricas_turmas'),
    path('gerar-codigo-turma/', views.gerar_codigo_turma, name='gerar_codigo_turma'),
]