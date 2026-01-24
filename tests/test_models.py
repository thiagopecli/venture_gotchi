"""
Testes unitários da Modelagem
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import User, Startup, Turma, Partida


class UserModelTests(TestCase):
    """Testes do modelo User"""
    
    def test_create_user(self):
        """Testa a criação de um usuário"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_method(self):
        """Testa a representação em string do usuário"""
        user = User.objects.create_user(
            username='testuser',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.assertIn('testuser', str(user))
    
    def test_user_categoria_choices(self):
        """Testa as opções de categoria de usuário"""
        user = User.objects.create_user(
            username='testuser',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.assertIn(user.categoria, [
            'ESTUDANTE_UNIVERSITARIO',
            'ASPIRANTE_EMPREENDEDOR',
            'EDUCADOR_NEGOCIOS',
            'PROFISSIONAL_CORPORATIVO'
        ])


class StartupModelTests(TestCase):
    """Testes do modelo Startup"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Company'
        )
    
    def test_create_startup(self):
        """Testa a criação de uma startup"""
        startup = Startup.objects.create(
            partida=self.partida,
            nome='Test Startup',
            saldo_caixa=100000
        )
        self.assertEqual(startup.nome, 'Test Startup')
        self.assertEqual(startup.saldo_caixa, 100000)
    
    def test_startup_validations(self):
        """Testa as validações do modelo Startup"""
        startup = Startup.objects.create(partida=self.partida, nome='Test')
        # Testa valores não negativos
        startup.funcionarios = -1
        with self.assertRaises(ValidationError):
            startup.full_clean()
    
    def test_startup_str_method(self):
        """Testa a representação em string da startup"""
        startup = Startup.objects.create(partida=self.partida, nome='My Startup')
        self.assertEqual(str(startup), 'My Startup')


class TurmaModelTests(TestCase):
    """Testes do modelo Turma"""
    
    def setUp(self):
        self.educador = User.objects.create_user(
            username='educador',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_create_turma(self):
        """Testa a criação de uma turma"""
        turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma de Teste',
            educador=self.educador
        )
        self.assertEqual(turma.codigo, 'ABC-123')
        self.assertEqual(turma.educador, self.educador)
    
    def test_turma_unique_codigo(self):
        """Testa se o código da turma é único"""
        Turma.objects.create(codigo='ABC-123', nome='Turma 1', educador=self.educador)
        with self.assertRaises(Exception):
            Turma.objects.create(codigo='ABC-123', nome='Turma 2', educador=self.educador)
