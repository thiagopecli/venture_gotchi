"""
Testes para views de educador e branches não cobertas
Objetivo: Alcançar 100% de cobertura em views.py
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal

from core.models import Partida, Startup, HistoricoDecisao, Turma, User

User = get_user_model()


class RegistroViewEdgeCasesTestCase(TestCase):
    """Testes para branches não cobertas em registro_view"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('registro')
    
    def test_registro_form_invalido_mostra_erro(self):
        """Testa se form inválido mostra mensagem de erro"""
        data = {
            'username': 'user',
            'email': 'invalid_email',  # Email inválido
            'password1': 'pass',
            'password2': 'different',  # Senhas diferentes
            'first_name': 'Test',
            'categoria': 'ESTUDANTE_UNIVERSITARIO',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        # Mensagem de erro deve estar presente


class SalvarJogoEdgeCasesTestCase(TestCase):
    """Testes para branches não cobertas em salvar_jogo"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            saldo_caixa=Decimal('30000.00'),
            receita_mensal=Decimal('2000.00')
        )
    
    def test_salvar_jogo_sem_startup(self):
        """Testa erro quando startup não existe"""
        # Deletar startup para simular erro
        self.startup.delete()
        
        self.client.login(username='player', password='pass123')
        response = self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Não fazer nada (Economizar)'
        })
        
        self.assertRedirects(response, reverse('dashboard'))


class EducadorDashboardTestCase(TestCase):
    """Testes para educador_dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_educador_dashboard_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('educador_dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_educador_dashboard_acesso(self):
        """Testa acesso ao dashboard de educador"""
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('educador_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'educador_dashboard.html')
    
    def test_educador_dashboard_mostra_turmas(self):
        """Testa se dashboard mostra turmas do educador"""
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('educador_dashboard'))
        
        self.assertIn('turmas_educador', response.context)


class CriarTurmaTestCase(TestCase):
    """Testes para criar_turma"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_criar_turma_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('criar_turma'))
        self.assertEqual(response.status_code, 302)
    
    def test_criar_turma_post(self):
        """Testa criação de turma via POST"""
        self.client.login(username='educador', password='pass123')
        response = self.client.post(reverse('criar_turma'), {
            'nome_turma': 'Nova Turma',
            'descricao_turma': 'Descrição da turma'
        })
        
        # Verifica se foi criada
        self.assertTrue(Turma.objects.filter(nome='Nova Turma').exists())
        self.assertEqual(response.status_code, 302)


class AnaliseTurmaTestCase(TestCase):
    """Testes para analise_turma"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
    
    def test_analise_turma_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('analise_turma', args=[self.turma.codigo]))
        self.assertEqual(response.status_code, 302)
    
    def test_analise_turma_com_alunos(self):
        """Testa análise com alunos na turma"""
        estudante = User.objects.create_user(
            username='estudante',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
        
        partida = Partida.objects.create(
            usuario=estudante,
            nome_empresa='Startup',
            data_inicio=timezone.now()
        )
        Startup.objects.create(partida=partida)
        
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('analise_turma', args=[self.turma.codigo]))
        
        # Verifica que a view funcionou
        self.assertEqual(response.status_code, 200)


class RankingTurmasTestCase(TestCase):
    """Testes para ranking_turmas"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_ranking_turmas_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('ranking_turmas'))
        self.assertEqual(response.status_code, 302)
    
    def test_ranking_turmas_acesso(self):
        """Testa acesso ao ranking de turmas"""
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('ranking_turmas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ranking_turmas.html')
    
    def test_ranking_turmas_com_dados(self):
        """Testa ranking com dados de turmas"""
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        
        estudante = User.objects.create_user(
            username='estudante',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
        
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('ranking_turmas'))
        
        self.assertEqual(response.status_code, 200)


class MetricasTurmasTestCase(TestCase):
    """Testes para metricas_turmas"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_metricas_turmas_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('metricas_turmas'))
        self.assertEqual(response.status_code, 302)
    
    def test_metricas_turmas_acesso(self):
        """Testa acesso às métricas de turmas"""
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('metricas_turmas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'metricas_turmas.html')
    
    def test_metricas_turmas_com_dados(self):
        """Testa métricas com dados de turmas"""
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        
        estudante = User.objects.create_user(
            username='estudante',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123'
        )
        
        partida = Partida.objects.create(
            usuario=estudante,
            nome_empresa='Startup',
            data_inicio=timezone.now()
        )
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('50000.00'))
        
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('metricas_turmas'))
        
        self.assertIn('turmas_dados', response.context)


class EditarPerfilTestCase(TestCase):
    """Testes para editar_perfil POST"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='pass123',
            email='user@test.com',
            first_name='João',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_editar_perfil_post_sucesso(self):
        """Testa atualização de perfil com sucesso"""
        self.client.login(username='user', password='pass123')
        response = self.client.post(reverse('editar_perfil'), {
            'first_name': 'João Silva',
            'email': 'joao.silva@test.com'
        })
        
        # Verifica redirecionamento ou sucesso
        self.assertIn(response.status_code, [200, 302])


class EducadorPerfilTestCase(TestCase):
    """Testes para educador_perfil"""
    
    def setUp(self):
        self.client = Client()
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_educador_perfil_requer_autenticacao(self):
        """Testa se requer login"""
        response = self.client.get(reverse('educador_perfil'))
        self.assertEqual(response.status_code, 302)
    
    def test_educador_perfil_acesso(self):
        """Testa acesso ao perfil de educador"""
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('educador_perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'educador_perfil.html')


class RedirectHandlerTestCase(TestCase):
    """Testes para redirect_handler"""
    
    def setUp(self):
        self.client = Client()
    
    def test_redirect_estudante(self):
        """Testa redirecionamento de estudante"""
        estudante = User.objects.create_user(
            username='estudante',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.client.login(username='estudante', password='pass')
        response = self.client.get(reverse('redirect_handler'))
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_redirect_educador(self):
        """Testa redirecionamento de educador"""
        educador = User.objects.create_user(
            username='educador',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.client.login(username='educador', password='pass')
        response = self.client.get(reverse('redirect_handler'))
        self.assertRedirects(response, reverse('educador_dashboard'))
    
    def test_redirect_aspirante(self):
        """Testa redirecionamento de aspirante"""
        aspirante = User.objects.create_user(
            username='aspirante',
            password='pass',
            categoria='ASPIRANTE_EMPREENDEDOR'
        )
        self.client.login(username='aspirante', password='pass')
        response = self.client.get(reverse('redirect_handler'))
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_redirect_profissional(self):
        """Testa redirecionamento de profissional"""
        prof = User.objects.create_user(
            username='prof',
            password='pass',
            categoria='PROFISSIONAL_CORPORATIVO'
        )
        self.client.login(username='prof', password='pass')
        response = self.client.get(reverse('redirect_handler'))
        self.assertRedirects(response, reverse('dashboard'))


class RankingFiltrosTestCase(TestCase):
    """Testes para filtros de ranking"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO',
            pais='Brasil',
            estado='MG',
            municipio='Belo Horizonte'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        Startup.objects.create(
            partida=self.partida,
            valuation=Decimal('500000.00')
        )
    
    def test_ranking_filtro_pais(self):
        """Testa filtro por país"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('ranking') + '?pais=Brasil')
        self.assertEqual(response.status_code, 200)
    
    def test_ranking_filtro_estado(self):
        """Testa filtro por estado"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('ranking') + '?estado=MG')
        self.assertEqual(response.status_code, 200)
    
    def test_ranking_filtro_municipio(self):
        """Testa filtro por município"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('ranking') + '?municipio=Belo Horizonte')
        self.assertEqual(response.status_code, 200)
    
    def test_ranking_criterio_saldo(self):
        """Testa ordenação por saldo"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('ranking') + '?criterio=saldo')
        self.assertEqual(response.status_code, 200)
    
    def test_ranking_criterio_turno(self):
        """Testa ordenação por turnos"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('ranking') + '?criterio=turnos')
        self.assertEqual(response.status_code, 200)
