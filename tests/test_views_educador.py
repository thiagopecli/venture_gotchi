"""
Testes de views específicas de educadores
Cobre dashboards, criação de turma, análise, métricas e relatórios
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Turma, Partida, Startup
from decimal import Decimal

User = get_user_model()


class EducadorDashboardTests(TestCase):
    """Testes do dashboard de educador"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.client.login(username='educador', password='testpass123')
    
    def test_dashboard_educador_acesso(self):
        """Testa acesso ao dashboard de educador"""
        response = self.client.get(reverse('educador_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'educador_dashboard.html')
    
    def test_dashboard_educador_exibe_turmas(self):
        """Testa que dashboard exibe turmas do educador"""
        turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma Teste',
            educador=self.educador
        )
        
        response = self.client.get(reverse('educador_dashboard'))
        self.assertContains(response, 'Turma Teste')
        self.assertContains(response, 'ABC-123')
    
    def test_dashboard_educador_sem_turmas(self):
        """Testa dashboard quando educador não tem turmas"""
        response = self.client.get(reverse('educador_dashboard'))
        self.assertContains(response, 'Nenhuma turma criada')
    
    def test_aluno_nao_acessa_dashboard_educador(self):
        """Testa que aluno não pode acessar dashboard de educador"""
        aluno = User.objects.create_user(
            username='aluno',
            email='aluno@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.client.login(username='aluno', password='testpass123')
        
        response = self.client.get(reverse('educador_dashboard'))
        self.assertNotEqual(response.status_code, 200)


class CriarTurmaTests(TestCase):
    """Testes de criação de turma"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.client.login(username='educador', password='testpass123')
    
    def test_criar_turma_sucesso(self):
        """Testa criação de turma com sucesso"""
        data = {
            'nome_turma': 'Nova Turma',
            'descricao_turma': 'Descrição da turma'
        }
        response = self.client.post(reverse('criar_turma'), data)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Turma.objects.filter(nome='Nova Turma').exists())
        
        turma = Turma.objects.get(nome='Nova Turma')
        self.assertEqual(turma.educador, self.educador)
        self.assertEqual(turma.descricao, 'Descrição da turma')
        self.assertTrue(turma.ativa)
    
    def test_criar_turma_sem_nome(self):
        """Testa que turma sem nome não é criada"""
        data = {
            'nome_turma': '',
            'descricao_turma': 'Descrição'
        }
        response = self.client.post(reverse('criar_turma'), data)
        
        self.assertFalse(Turma.objects.filter(descricao='Descrição').exists())
    
    def test_criar_turma_codigo_unico(self):
        """Testa que cada turma recebe código único"""
        data1 = {'nome_turma': 'Turma 1', 'descricao_turma': ''}
        data2 = {'nome_turma': 'Turma 2', 'descricao_turma': ''}
        
        self.client.post(reverse('criar_turma'), data1)
        self.client.post(reverse('criar_turma'), data2)
        
        turma1 = Turma.objects.get(nome='Turma 1')
        turma2 = Turma.objects.get(nome='Turma 2')
        
        self.assertNotEqual(turma1.codigo, turma2.codigo)
    
    def test_aluno_nao_pode_criar_turma(self):
        """Testa que aluno não pode criar turma"""
        aluno = User.objects.create_user(
            username='aluno',
            email='aluno@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.client.login(username='aluno', password='testpass123')
        
        data = {'nome_turma': 'Turma Teste', 'descricao_turma': ''}
        response = self.client.post(reverse('criar_turma'), data)
        
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Turma.objects.filter(nome='Turma Teste').exists())


class AnaliseTurmaTests(TestCase):
    """Testes de análise de turma"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma Teste',
            educador=self.educador
        )
        self.client.login(username='educador', password='testpass123')
    
    def test_analise_turma_acesso(self):
        """Testa acesso à página de análise de turma"""
        response = self.client.get(reverse('analise_turma', args=['ABC-123']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analise_turma.html')
    
    def test_analise_turma_exibe_dados(self):
        """Testa que análise exibe dados da turma"""
        response = self.client.get(reverse('analise_turma', args=['ABC-123']))
        self.assertContains(response, 'Turma Teste')
        self.assertContains(response, 'ABC-123')
    
    def test_analise_turma_com_alunos(self):
        """Testa análise de turma com alunos"""
        aluno = User.objects.create_user(
            username='aluno',
            email='aluno@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
        partida = Partida.objects.create(
            usuario=aluno,
            nome_empresa='Startup Teste'
        )
        startup = Startup.objects.create(
            partida=partida,
            nome='Startup Teste',
            saldo_caixa=Decimal('50000.00')
        )
        
        response = self.client.get(reverse('analise_turma', args=['ABC-123']))
        self.assertContains(response, 'Startup Teste')
    
    def test_analise_turma_inexistente(self):
        """Testa acesso a turma inexistente"""
        response = self.client.get(reverse('analise_turma', args=['XYZ-999']))
        self.assertEqual(response.status_code, 404)
    
    def test_educador_nao_ve_turma_de_outro(self):
        """Testa que educador não vê análise de turma de outro educador"""
        outro_educador = User.objects.create_user(
            username='outro',
            email='outro@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        turma_outro = Turma.objects.create(
            codigo='XYZ-789',
            nome='Turma Outro',
            educador=outro_educador
        )
        
        response = self.client.get(reverse('analise_turma', args=['XYZ-789']))
        # Deve retornar 404 ou redirecionar, não 200
        self.assertNotEqual(response.status_code, 200)


class RankingTurmasTests(TestCase):
    """Testes de ranking de turmas"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.client.login(username='educador', password='testpass123')
    
    def test_ranking_turmas_acesso(self):
        """Testa acesso ao ranking de turmas"""
        response = self.client.get(reverse('ranking_turmas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ranking_turmas.html')
    
    def test_ranking_turmas_exibe_turmas_educador(self):
        """Testa que ranking exibe apenas turmas do educador"""
        turma1 = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma 1',
            educador=self.educador
        )
        turma2 = Turma.objects.create(
            codigo='DEF-456',
            nome='Turma 2',
            educador=self.educador
        )
        
        # Turma de outro educador
        outro_educador = User.objects.create_user(
            username='outro',
            email='outro@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        turma_outro = Turma.objects.create(
            codigo='XYZ-789',
            nome='Turma Outro',
            educador=outro_educador
        )
        
        response = self.client.get(reverse('ranking_turmas'))
        self.assertContains(response, 'Turma 1')
        self.assertContains(response, 'Turma 2')
        self.assertNotContains(response, 'Turma Outro')


class MetricasTurmasTests(TestCase):
    """Testes de métricas agregadas de turmas"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.turma = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma Teste',
            educador=self.educador
        )
        self.client.login(username='educador', password='testpass123')
    
    def test_metricas_turmas_acesso(self):
        """Testa acesso à página de métricas"""
        response = self.client.get(reverse('metricas_turmas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'metricas_turmas.html')
    
    def test_metricas_turmas_com_dados(self):
        """Testa métricas com dados de alunos"""
        aluno = User.objects.create_user(
            username='aluno',
            email='aluno@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
        partida = Partida.objects.create(
            usuario=aluno,
            nome_empresa='Startup Teste'
        )
        startup = Startup.objects.create(
            partida=partida,
            nome='Startup Teste',
            saldo_caixa=Decimal('100000.00')
        )
        
        response = self.client.get(reverse('metricas_turmas'))
        self.assertEqual(response.status_code, 200)


class GerarCodigoTurmaTests(TestCase):
    """Testes de geração de código de turma"""
    
    def test_codigo_formato_correto(self):
        """Testa que código gerado tem formato AAA-999"""
        import re
        codigo = Turma.gerar_codigo_unico()
        self.assertIsNotNone(re.match(r'^[A-Z]{3}-[0-9]{3}$', codigo))
    
    def test_codigos_sao_unicos(self):
        """Testa que códigos gerados são únicos"""
        codigos = set()
        for _ in range(10):
            codigo = Turma.gerar_codigo_unico()
            self.assertNotIn(codigo, codigos)
            codigos.add(codigo)
    
    def test_codigo_nao_repete_existente(self):
        """Testa que código gerado não repete código existente no banco"""
        educador = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        
        # Criar turma com código específico
        turma1 = Turma.objects.create(
            codigo='ABC-123',
            nome='Turma 1',
            educador=educador
        )
        
        # Gerar novo código deve ser diferente
        novo_codigo = Turma.gerar_codigo_unico()
        self.assertNotEqual(novo_codigo, 'ABC-123')
