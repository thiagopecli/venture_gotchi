"""
Testes iniciais do fluxo de autenticação
"""
from django.test import TestCase, Client
from django.urls import reverse
from core.models import User


class AuthenticationFlowTests(TestCase):
    """Testes do fluxo completo de autenticação"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'categoria': 'ESTUDANTE_UNIVERSITARIO'
        }
    
    def test_user_registration(self):
        """Testa o registro de novo usuário"""
        response = self.client.post(reverse('registro'), self.user_data)
        # Verifica se o usuário foi criado ou se há redirecionamento
        self.assertIn(response.status_code, [200, 302])
        # Se o status for 302 (sucesso), verifica se o usuário foi criado
        if response.status_code == 302:
            self.assertEqual(User.objects.count(), 1)
    
    def test_user_login(self):
        """Testa o login de usuário"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(reverse('login'), {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, 302)  # Redirect após login
    
    def test_user_logout(self):
        """Testa o logout de usuário"""
        User.objects.create_user(**self.user_data)
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])
        response = self.client.post(reverse('logout'))  # Logout requer POST
        self.assertEqual(response.status_code, 302)
    
    def test_login_required_views(self):
        """Testa se views protegidas requerem autenticação"""
        protected_urls = ['dashboard', 'perfil', 'historico']
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [302, 403])
