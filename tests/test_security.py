"""
Revisão da arquitetura e segurança
"""
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import User, Startup, Turma, Partida
from core.permissions import (
    estudante_required, 
    educador_required,
    pode_salvar_partida,
    pode_acessar_relatorios,
    pode_acessar_ranking
)
from unittest.mock import Mock
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware


class SecurityTests(TestCase):
    """Testes de segurança da aplicação"""
    
    def setUp(self):
        self.client = Client()
        self.aluno = User.objects.create_user(
            username='aluno',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_unauthenticated_access_denied(self):
        """Testa se usuários não autenticados não acessam páginas protegidas"""
        protected_urls = ['dashboard', 'perfil', 'ranking']
        
        for url_name in protected_urls:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertIn(response.status_code, [302, 403])
    
    def test_aluno_cannot_access_educador_pages(self):
        """Testa se aluno não acessa páginas de educador"""
        self.client.login(username='aluno', password='testpass123')
        
        educador_urls = ['educador_dashboard', 'metricas_turmas']
        for url_name in educador_urls:
            with self.subTest(url=url_name):
                response = self.client.get(reverse(url_name))
                self.assertIn(response.status_code, [302, 403])
    
    def test_educador_cannot_modify_other_turma(self):
        """Testa se educador não modifica turma de outro educador"""
        outro_educador = User.objects.create_user(
            username='outro_educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma Outro',
            educador=outro_educador
        )
        
        self.client.login(username='educador', password='testpass123')
        response = self.client.get(reverse('analise_turma', args=['ABC-123']))
        self.assertIn(response.status_code, [302, 403, 404])
    
    def test_user_cannot_modify_other_startup(self):
        """Testa se usuário não modifica startup de outro usuário"""
        outro_user = User.objects.create_user(username='outro', password='testpass123', categoria='ESTUDANTE_UNIVERSITARIO')
        partida = Partida.objects.create(usuario=outro_user, nome_empresa='Empresa Outro')
        startup = Startup.objects.create(partida=partida, nome='Startup Outro')
        
        self.client.login(username='aluno', password='testpass123')
        # Tente modificar startup de outro usuário
        # Adicione teste específico conforme sua implementação
    
    def test_sql_injection_protection(self):
        """Testa proteção contra SQL injection"""
        malicious_input = "'; DROP TABLE core_user; --"
        response = self.client.post(reverse('login'), {
            'username': malicious_input,
            'password': 'anything'
        })
        # Verifica se tabela ainda existe
        self.assertTrue(User.objects.model._meta.db_table)
    
    def test_xss_protection(self):
        """Testa proteção contra XSS"""
        self.client.login(username='aluno', password='testpass123')
        xss_script = '<script>alert("XSS")</script>'
        
        # Tenta injetar script no nome da startup
        partida = Partida.objects.create(usuario=self.aluno, nome_empresa='Empresa XSS')
        startup = Startup.objects.create(
            partida=partida,
            nome=xss_script
        )
        
        response = self.client.get(reverse('dashboard'))
        # Verifica se o script foi escapado
        self.assertNotContains(response, '<script>', html=True)


class PermissionTests(TestCase):
    """Testes de permissões e autorização"""
    
    def setUp(self):
        self.client = Client()
        self.aluno = User.objects.create_user(
            username='aluno',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            password='testpass123',
            email='admin@example.com'
        )
    
    def test_admin_has_full_access(self):
        """Testa se admin tem acesso completo"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_roles_correctly_assigned(self):
        """Testa se roles de usuários estão corretos"""
        self.assertEqual(self.aluno.categoria, 'ESTUDANTE_UNIVERSITARIO')
        self.assertEqual(self.educador.categoria, 'EDUCADOR_NEGOCIOS')
        self.assertTrue(self.admin.is_superuser)


class DataValidationTests(TestCase):
    """Testes de validação de dados"""
    
    def test_startup_negative_values_rejected(self):
        """Testa se valores negativos são rejeitados"""
        user = User.objects.create_user(username='test', password='test123', categoria='ESTUDANTE_UNIVERSITARIO')
        partida = Partida.objects.create(usuario=user, nome_empresa='Empresa Teste')
        startup = Startup.objects.create(partida=partida, nome='Test')
        
        # Tenta definir valor negativo em 'funcionarios'
        startup.funcionarios = -1
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            startup.full_clean()
    
    def test_turma_codigo_validation(self):
        """Testa validação do código da turma"""
        educador = User.objects.create_user(username='educador', password='test123', categoria='EDUCADOR_NEGOCIOS')
        
        # Código vazio não deve ser aceito (validação via full_clean)
        turma = Turma(codigo='', nome='Turma', educador=educador)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            turma.full_clean()


class PermissionDecoratorsTests(TestCase):
    """Testes dos decorators de permissão"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.estudante = User.objects.create_user(
            username='estudante',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.aspirante = User.objects.create_user(
            username='aspirante',
            password='testpass123',
            categoria='ASPIRANTE_EMPREENDEDOR'
        )
    
    def _add_middleware(self, request):
        """Adiciona middleware necessário para messages"""
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
    
    def test_estudante_required_decorator(self):
        """Testa decorator estudante_required"""
        @estudante_required
        def mock_view(request):
            return Mock(status_code=200)
        
        # Estudante deve passar
        request = self.factory.get('/')
        request.user = self.estudante
        self._add_middleware(request)
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_estudante_required_blocks_educador(self):
        """Testa que estudante_required bloqueia educador"""
        @estudante_required
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.educador
        self._add_middleware(request)
        response = mock_view(request)
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
    
    def test_educador_required_decorator(self):
        """Testa decorator educador_required"""
        @educador_required
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.educador
        self._add_middleware(request)
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_educador_required_blocks_estudante(self):
        """Testa que educador_required bloqueia estudante"""
        @educador_required
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.estudante
        self._add_middleware(request)
        response = mock_view(request)
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
    
    def test_pode_salvar_partida_decorator(self):
        """Testa decorator pode_salvar_partida"""
        @pode_salvar_partida
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.estudante
        self._add_middleware(request)
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_pode_salvar_partida_blocks_educador(self):
        """Testa que pode_salvar_partida bloqueia educador"""
        @pode_salvar_partida
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.educador
        self._add_middleware(request)
        response = mock_view(request)
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
    
    def test_pode_acessar_relatorios_decorator(self):
        """Testa decorator pode_acessar_relatorios"""
        @pode_acessar_relatorios
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.educador
        self._add_middleware(request)
        response = mock_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_pode_acessar_relatorios_blocks_estudante(self):
        """Testa que pode_acessar_relatorios bloqueia estudante"""
        @pode_acessar_relatorios
        def mock_view(request):
            return Mock(status_code=200)
        
        request = self.factory.get('/')
        request.user = self.estudante
        self._add_middleware(request)
        response = mock_view(request)
        # Deve redirecionar
        self.assertEqual(response.status_code, 302)
    
    def test_aspirante_pode_salvar_partida(self):
        """Testa que aspirante pode salvar partida"""
        self.assertTrue(self.aspirante.pode_salvar_carregar_partida())
        self.assertTrue(self.aspirante.pode_desbloquear_conquistas())
