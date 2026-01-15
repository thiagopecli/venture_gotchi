"""
Testes do Sistema de Permissões
"""
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Partida, Startup
from decimal import Decimal


class PermissoesTestCase(TestCase):
    """Testes para o sistema de permissões"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        
        # Criar usuário estudante
        self.estudante = User.objects.create_user(
            username='estudante_teste',
            email='estudante@teste.com',
            password='senha123',
            documento='12345678901',
            categoria=User.Categorias.ALUNO
        )
        
        # Criar usuário educador
        self.educador = User.objects.create_user(
            username='educador_teste',
            email='educador@teste.com',
            password='senha123',
            documento='98765432100',
            categoria=User.Categorias.PROFESSOR
        )
    
    def test_estudante_pode_criar_partida(self):
        """Testa se estudante pode criar partida"""
        self.client.login(username='estudante_teste', password='senha123')
        
        response = self.client.post(reverse('nova_partida'), {
            'nome_empresa': 'Startup Teste',
            'saldo_inicial': '50000'
        })
        
        # Verifica se a partida foi criada
        self.assertEqual(Partida.objects.filter(usuario=self.estudante).count(), 1)
    
    def test_educador_nao_pode_criar_partida(self):
        """Testa se educador NÃO pode criar partida"""
        self.client.login(username='educador_teste', password='senha123')
        
        response = self.client.post(reverse('nova_partida'), {
            'nome_empresa': 'Startup Teste',
            'saldo_inicial': '50000'
        })
        
        # Verifica se foi redirecionado
        self.assertEqual(response.status_code, 302)
        # Verifica se nenhuma partida foi criada
        self.assertEqual(Partida.objects.filter(usuario=self.educador).count(), 0)
    
    def test_metodos_permissao_estudante(self):
        """Testa métodos de permissão para estudante"""
        self.assertTrue(self.estudante.is_estudante())
        self.assertFalse(self.estudante.is_educador())
        self.assertTrue(self.estudante.pode_salvar_carregar_partida())
        self.assertTrue(self.estudante.pode_visualizar_propria_partida())
        self.assertFalse(self.estudante.pode_acessar_relatorios_agregados())
        self.assertTrue(self.estudante.pode_acessar_ranking())
        self.assertTrue(self.estudante.pode_desbloquear_conquistas())
    
    def test_metodos_permissao_educador(self):
        """Testa métodos de permissão para educador"""
        self.assertFalse(self.educador.is_estudante())
        self.assertTrue(self.educador.is_educador())
        self.assertFalse(self.educador.pode_salvar_carregar_partida())
        self.assertFalse(self.educador.pode_visualizar_propria_partida())
        self.assertTrue(self.educador.pode_acessar_relatorios_agregados())
        self.assertTrue(self.educador.pode_acessar_ranking())
        self.assertFalse(self.educador.pode_desbloquear_conquistas())
    
    def test_dashboard_estudante(self):
        """Testa se dashboard mostra conteúdo correto para estudante"""
        self.client.login(username='estudante_teste', password='senha123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Minhas Simulações')
        self.assertContains(response, 'Iniciar Nova Startup')
    
    def test_dashboard_educador(self):
        """Testa se dashboard mostra conteúdo correto para educador"""
        self.client.login(username='educador_teste', password='senha123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Painel do Educador')
        self.assertContains(response, 'Funcionalidades de Educador')
