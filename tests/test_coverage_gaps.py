"""
Testes para cobrir os últimos gaps de cobertura e atingir 100%
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from core.permissions import estudante_required, educador_required, pode_salvar_partida, pode_acessar_relatorios, pode_acessar_ranking
from core.models import User, Evento, Fundador, Partida
from core.templatetags.custom_filters import moeda_br
from decimal import Decimal, InvalidOperation

User = get_user_model()


class PermissionsUnauthenticatedTestCase(TestCase):
    """Testes para usuários não autenticados nos decoradores"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def _add_middleware_to_request(self, request):
        """Adiciona middleware de mensagens e sessão ao request"""
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda x: x)
        middleware.process_request(request)
    
    def test_estudante_required_usuario_nao_autenticado(self):
        """Testa @estudante_required com usuário não autenticado"""
        @estudante_required
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = AnonymousUser()
        response = view(request)
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_educador_required_usuario_nao_autenticado(self):
        """Testa @educador_required com usuário não autenticado"""
        @educador_required
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = AnonymousUser()
        response = view(request)
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_pode_salvar_partida_usuario_nao_autenticado(self):
        """Testa @pode_salvar_partida com usuário não autenticado"""
        @pode_salvar_partida
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = AnonymousUser()
        response = view(request)
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_pode_acessar_relatorios_usuario_nao_autenticado(self):
        """Testa @pode_acessar_relatorios com usuário não autenticado"""
        @pode_acessar_relatorios
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = AnonymousUser()
        response = view(request)
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_pode_acessar_ranking_usuario_nao_autenticado(self):
        """Testa @pode_acessar_ranking com usuário não autenticado"""
        @pode_acessar_ranking
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = AnonymousUser()
        response = view(request)
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class ModelsMissingLinesTestCase(TestCase):
    """Testes para cobrir linhas faltantes em models.py"""
    
    def test_fundador_str(self):
        """Testa __str__ do modelo Fundador (linha 292)"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        partida = Partida.objects.create(
            usuario=user,
            nome_empresa='Test Startup'
        )
        fundador = Fundador.objects.create(
            partida=partida,
            nome='João Silva',
            idade=30,
            experiencia='tecnologia',
            anos_experiencia=5
        )
        # Verifica se o __str__ funciona corretamente
        str_repr = str(fundador)
        self.assertIn('João Silva', str_repr)
        self.assertIn('Tecnologia', str_repr)


class TemplateFilterExceptionTestCase(TestCase):
    """Testes para cobrir exception handling em custom_filters.py"""
    
    def test_moeda_br_attribute_error(self):
        """Testa tratamento de AttributeError em moeda_br (linha 29)"""
        # Object sem atributos relevantes causa AttributeError
        class ObjSemAttr:
            def __str__(self):
                return "objeto"
        
        result = moeda_br(ObjSemAttr())
        self.assertEqual(result, 'R$ 0,00')
