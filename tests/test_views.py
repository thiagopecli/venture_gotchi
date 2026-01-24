"""
Testes simplificados para views cobrindo funcionalidades críticas.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal

from core.models import Partida, Startup, HistoricoDecisao, Turma, Conquista, ConquistaDesbloqueada
from core.views import formatar_moeda_br

User = get_user_model()


class FormatamoedaBrTestCase(TestCase):
    """Testes para função formatar_moeda_br"""
    
    def test_formata_valor_inteiro(self):
        resultado = formatar_moeda_br(1234567)
        self.assertEqual(resultado, 'R$ 1.234.567,00')
    
    def test_formata_decimal(self):
        resultado = formatar_moeda_br(Decimal('1234.56'))
        self.assertEqual(resultado, 'R$ 1.234,56')
    
    def test_formata_zero(self):
        resultado = formatar_moeda_br(0)
        self.assertEqual(resultado, 'R$ 0,00')
    
    def test_formata_none(self):
        resultado = formatar_moeda_br(None)
        self.assertEqual(resultado, 'R$ 0,00')
    
    def test_formata_negativo(self):
        resultado = formatar_moeda_br(Decimal('-1000.00'))
        self.assertEqual(resultado, 'R$ -1.000,00')


class DashboardViewTestCase(TestCase):
    """Testes para view de dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.estudante = User.objects.create_user(
            username='estudante', 
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_dashboard_requer_autenticacao(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_estudante(self):
        self.client.login(username='estudante', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
    
    def test_dashboard_educador_redireciona(self):
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_mostra_partidas(self):
        Partida.objects.create(
            usuario=self.estudante,
            nome_empresa='Startup 1',
            data_inicio=timezone.now()
        )
        Partida.objects.create(
            usuario=self.estudante,
            nome_empresa='Startup 2',
            data_inicio=timezone.now()
        )
        
        self.client.login(username='estudante', password='pass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(len(response.context['partidas']), 2)


class NovaPartidaViewTestCase(TestCase):
    """Testes para criação de nova partida"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_nova_partida_requer_autenticacao(self):
        response = self.client.get(reverse('nova_partida'))
        self.assertEqual(response.status_code, 302)
    
    def test_nova_partida_get(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('nova_partida'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nova_partida.html')
    
    def test_nova_partida_criacao(self):
        self.client.login(username='player', password='pass123')
        response = self.client.post(reverse('nova_partida'), {
            'nome_empresa': 'Minha Startup'
        })
        
        partida = Partida.objects.get(nome_empresa='Minha Startup')
        self.assertRedirects(response, reverse('carregar_jogo', args=[partida.id]))
        
        startup = Startup.objects.get(partida=partida)
        self.assertEqual(startup.saldo_caixa, Decimal('30000.00'))


class SalvarJogoViewTestCase(TestCase):
    """Testes para salvar jogo e aplicar decisões"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup',
            data_inicio=timezone.now()
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            saldo_caixa=Decimal('30000.00'),
            receita_mensal=Decimal('2000.00'),
            funcionarios=0
        )
    
    def test_salvar_jogo_marketing(self):
        self.client.login(username='player', password='pass123')
        self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Investir em Marketing Agressivo'
        })
        
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.saldo_caixa, Decimal('27000.00'))
        self.assertEqual(self.startup.receita_mensal, Decimal('5000.00'))
    
    def test_salvar_jogo_engenheiro(self):
        self.client.login(username='player', password='pass123')
        self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Contratar Engenheiro Sênior'
        })
        
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.saldo_caixa, Decimal('24000.00'))
        self.assertEqual(self.startup.funcionarios, 1)
    
    def test_salvar_jogo_economizar(self):
        self.client.login(username='player', password='pass123')
        self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Não fazer nada (Economizar)'
        })
        
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.saldo_caixa, Decimal('32000.00'))
    
    def test_salvar_jogo_saldo_insuficiente(self):
        self.startup.saldo_caixa = Decimal('100.00')
        self.startup.receita_mensal = Decimal('500.00')
        self.startup.save()
        
        self.client.login(username='player', password='pass123')
        self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Investir em Marketing Agressivo'
        })
        
        self.startup.refresh_from_db()
        self.assertEqual(self.startup.saldo_caixa, Decimal('100.00'))
    
    def test_salvar_jogo_partida_inativa(self):
        self.partida.ativa = False
        self.partida.save()
        
        self.client.login(username='player', password='pass123')
        response = self.client.post(reverse('salvar_jogo', args=[self.partida.id]), {
            'decisao': 'Não fazer nada (Economizar)'
        })
        
        self.assertRedirects(response, reverse('carregar_jogo', args=[self.partida.id]))


class CarregarJogoViewTestCase(TestCase):
    """Testes para carregar estado do jogo"""
    
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
            saldo_caixa=Decimal('30000.00')
        )
    
    def test_carregar_jogo_requer_autenticacao(self):
        response = self.client.get(reverse('carregar_jogo', args=[self.partida.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_carregar_jogo_sucesso(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('carregar_jogo', args=[self.partida.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'jogo.html')
    
    def test_carregar_jogo_game_over(self):
        self.startup.saldo_caixa = Decimal('-100.00')
        self.startup.save()
        
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('carregar_jogo', args=[self.partida.id]))
        
        self.assertTrue(response.context['game_over'])
        self.partida.refresh_from_db()
        self.assertFalse(self.partida.ativa)
    
    def test_carregar_jogo_vitoria(self):
        self.startup.valuation = Decimal('1500000.00')
        self.startup.save()
        
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('carregar_jogo', args=[self.partida.id]))
        
        self.assertTrue(response.context['vitoria'])
        self.partida.refresh_from_db()
        self.assertFalse(self.partida.ativa)


class PerfilViewTestCase(TestCase):
    """Testes para view de perfil"""
    
    def setUp(self):
        self.client = Client()
        self.estudante = User.objects.create_user(
            username='estudante',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.educador = User.objects.create_user(
            username='educador',
            password='pass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_perfil_requer_autenticacao(self):
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 302)
    
    def test_perfil_estudante(self):
        self.client.login(username='estudante', password='pass123')
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'perfil.html')
    
    def test_perfil_educador_bloqueado(self):
        self.client.login(username='educador', password='pass123')
        response = self.client.get(reverse('perfil'))
        self.assertEqual(response.status_code, 302)
    
    def test_perfil_mostra_estatisticas(self):
        Partida.objects.create(
            usuario=self.estudante,
            nome_empresa='Startup 1',
            ativa=True,
            data_inicio=timezone.now()
        )
        Partida.objects.create(
            usuario=self.estudante,
            nome_empresa='Startup 2',
            ativa=False,
            data_inicio=timezone.now()
        )
        
        self.client.login(username='estudante', password='pass123')
        response = self.client.get(reverse('perfil'))
        
        self.assertEqual(response.context['total_partidas'], 2)
        self.assertEqual(response.context['partidas_ativas'], 1)
        self.assertEqual(response.context['partidas_finalizadas'], 1)


class HistoricoViewTestCase(TestCase):
    """Testes para view de histórico de decisões"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup',
            data_inicio=timezone.now()
        )
    
    def test_historico_requer_autenticacao(self):
        response = self.client.get(reverse('historico'))
        self.assertEqual(response.status_code, 302)
    
    def test_historico_vazio(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('historico'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historico.html')
    
    def test_historico_com_decisoes(self):
        HistoricoDecisao.objects.create(
            partida=self.partida,
            decisao_tomada='Investir em Marketing Agressivo',
            turno=1
        )
        HistoricoDecisao.objects.create(
            partida=self.partida,
            decisao_tomada='Contratar Engenheiro Sênior',
            turno=2
        )
        
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('historico'))
        
        decisoes_por_empresa = response.context['decisoes_por_empresa']
        self.assertEqual(len(decisoes_por_empresa), 1)
        self.assertEqual(decisoes_por_empresa[0]['total_decisoes'], 2)


class ConquistasViewTestCase(TestCase):
    """Testes para view de conquistas"""
    
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
        Startup.objects.create(partida=self.partida)
        
        self.conquista = Conquista.objects.create(
            titulo='Primeira Vitória',
            descricao='Vencer a primeira partida',
            pontos=100
        )
    
    def test_conquistas_requer_autenticacao(self):
        response = self.client.get(reverse('conquistas'))
        self.assertEqual(response.status_code, 302)
    
    def test_conquistas_vazio(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('conquistas'))
        self.assertEqual(response.status_code, 200)
    
    def test_conquistas_desbloqueadas(self):
        ConquistaDesbloqueada.objects.create(
            partida=self.partida,
            conquista=self.conquista
        )
        
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('conquistas'))
        
        conquistas_por_empresa = response.context['conquistas_por_empresa']
        self.assertEqual(len(conquistas_por_empresa), 1)


class MetricasViewTestCase(TestCase):
    """Testes para view de métricas de partida"""
    
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
            saldo_caixa=Decimal('50000.00')
        )
    
    def test_metricas_requer_autenticacao(self):
        response = self.client.get(reverse('metricas', args=[self.partida.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_metricas_sucesso(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('metricas', args=[self.partida.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'metricas.html')


class RankingViewTestCase(TestCase):
    """Testes para view de ranking"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_ranking_requer_autenticacao(self):
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 302)
    
    def test_ranking_acesso(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ranking.html')
    
    def test_ranking_ordenacao_valuation(self):
        p1 = Partida.objects.create(usuario=self.user, nome_empresa='Startup A', data_inicio=timezone.now())
        Startup.objects.create(partida=p1, valuation=Decimal('100000.00'))
        
        p2 = Partida.objects.create(usuario=self.user, nome_empresa='Startup B', data_inicio=timezone.now())
        Startup.objects.create(partida=p2, valuation=Decimal('500000.00'))
        
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('ranking') + '?criterio=valuation')
        
        self.assertEqual(response.status_code, 200)


class EditarPerfilViewTestCase(TestCase):
    """Testes para editar perfil do usuário"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='player',
            password='pass123',
            first_name='João',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_editar_perfil_requer_autenticacao(self):
        response = self.client.get(reverse('editar_perfil'))
        self.assertEqual(response.status_code, 302)
    
    def test_editar_perfil_get(self):
        self.client.login(username='player', password='pass123')
        response = self.client.get(reverse('editar_perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editar_perfil.html')
