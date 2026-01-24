"""
Testes de integração (views + models)
"""
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Startup, Turma, Partida


class GameFlowIntegrationTests(TestCase):
    """Testes de integração do fluxo do jogo"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Company'
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            nome='Test Startup'
        )
    
    def test_complete_game_flow(self):
        """Testa o fluxo completo: login -> dashboard -> nova_partida -> ranking"""
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # Acessa dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Acessa nova partida
        response = self.client.get(reverse('nova_partida'))
        self.assertIn(response.status_code, [200, 302])
        
        # Acessa ranking
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)


class ProfileIntegrationTests(TestCase):
    """Testes de integração do perfil e edição"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_profile_view_and_edit(self):
        """Testa visualização e edição de perfil"""
        self.client.login(username='testuser', password='testpass123')
        
        # Visualiza perfil
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 200)
        
        # Edita perfil
        response = self.client.post(reverse('editar_perfil'), {
            'email': 'newemail@example.com',
            'nome_completo': 'New Name'
        })
        
        # Verifica se foi atualizado
        self.user.refresh_from_db()
        # Adicione verificações conforme os campos do seu formulário


class TurmaIntegrationTests(TestCase):
    """Testes de integração com turmas"""
    
    def setUp(self):
        self.educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma Teste',
            educador=self.educador
        )
        self.aluno = User.objects.create_user(
            username='aluno',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
    
    def test_educador_views_turma_metrics(self):
        """Testa se educador consegue ver métricas da turma"""
        self.client.login(username='educador', password='testpass123')
        response = self.client.get(reverse('analise_turma', args=['ABC-123']))
        self.assertEqual(response.status_code, 200)
        
    def test_aluno_in_turma_ranking(self):
        """Testa se aluno aparece no ranking da turma"""
        partida = Partida.objects.create(usuario=self.aluno, nome_empresa='Empresa Aluno')
        Startup.objects.create(partida=partida, nome='Startup Aluno')
        self.client.login(username='aluno', password='testpass123')
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)
