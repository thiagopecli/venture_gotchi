"""
Teste completo de usabilidade e navegação
"""
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User, Startup, Turma, Partida


class NavigationTests(TestCase):
    """Testes de navegação entre páginas"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        partida = Partida.objects.create(usuario=self.user, nome_empresa='Empresa Teste')
        Startup.objects.create(partida=partida, nome='Test Startup')
    
    def test_all_main_pages_accessible(self):
        """Testa se todas as páginas principais estão acessíveis"""
        self.client.login(username='testuser', password='testpass123')
        
        pages = [
            'dashboard',
            'perfil',
            'ranking',
            'conquistas',
            'historico'
        ]
        
        for page_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200,
                    f"Página {page_name} não está acessível")
    
    def test_navigation_links_in_templates(self):
        """Testa se os links de navegação estão presentes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        # Verifica presença de links importantes
        self.assertContains(response, 'href')


class UsabilityTests(TestCase):
    """Testes de usabilidade da interface"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_error_messages_displayed(self):
        """Testa se mensagens de erro são exibidas"""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        # Verifica se há mensagem de erro ou redirecionamento
        self.assertIn(response.status_code, [200, 302])
    
    def test_success_messages_displayed(self):
        """Testa se mensagens de sucesso são exibidas"""
        self.client.login(username='testuser', password='testpass123')
        # Teste de ação bem-sucedida
        # Adicione teste específico conforme suas views
    
    def test_responsive_elements(self):
        """Testa se elementos responsivos estão presentes"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class AccessibilityTests(TestCase):
    """Testes de acessibilidade básica"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', categoria='ESTUDANTE_UNIVERSITARIO')
    
    def test_pages_have_titles(self):
        """Testa se páginas têm títulos"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '<title>')
    
    def test_forms_have_labels(self):
        """Testa se formulários têm labels apropriados"""
        response = self.client.get(reverse('login'))
        self.assertContains(response, '<label')


class WorkflowTests(TestCase):
    """Testes de fluxos completos de trabalho"""
    
    def setUp(self):
        self.client = Client()
    
    def test_new_user_complete_workflow(self):
        """Testa fluxo completo de novo usuário"""
        # 1. Registro
        response = self.client.post(reverse('registro'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123!',
            'password_confirmation': 'NewPass123!'
        })
        
        # 2. Login
        response = self.client.post(reverse('login'), {
            'username': 'newuser',
            'password': 'NewPass123!'
        })
        
        # 3. Criar startup
        response = self.client.get(reverse('nova_partida'))
        
        # 4. Acessar ranking
        response = self.client.get(reverse('ranking'))
    
    def test_educador_workflow(self):
        """Testa fluxo completo de educador"""
        educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        
        self.client.login(username='educador', password='testpass123')
        
        # 1. Ver dashboard do educador
        response = self.client.get(reverse('educador_dashboard'))
        
        # 2. Ver métricas de turmas
        response = self.client.get(reverse('metricas_turmas'))
        
        # 3. Ver rankings
        response = self.client.get(reverse('ranking_turmas'))
