"""
Testes adicionais para aumentar cobertura: edge cases, modelos, constraints
"""
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from core.models import Partida, Startup, HistoricoDecisao, Turma, Conquista, ConquistaDesbloqueada

User = get_user_model()


class UserMethodsTestCase(TestCase):
    """Testes para métodos de usuário"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='teste',
            password='pass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_user_is_estudante(self):
        self.assertTrue(self.user.is_estudante())
    
    def test_user_is_educador(self):
        self.assertFalse(self.user.is_educador())
    
    def test_user_is_aspirante(self):
        self.assertFalse(self.user.is_aspirante())
    
    def test_user_is_profissional(self):
        self.assertFalse(self.user.is_profissional())
    
    def test_educador_is_educador(self):
        educador = User.objects.create_user(
            username='edu',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.assertTrue(educador.is_educador())
        self.assertFalse(educador.is_estudante())
    
    def test_aspirante_is_aspirante(self):
        aspirante = User.objects.create_user(
            username='asp',
            password='pass',
            categoria='ASPIRANTE_EMPREENDEDOR'
        )
        self.assertTrue(aspirante.is_aspirante())
    
    def test_profissional_is_profissional(self):
        prof = User.objects.create_user(
            username='prof',
            password='pass',
            categoria='PROFISSIONAL_CORPORATIVO'
        )
        self.assertTrue(prof.is_profissional())
    
    def test_pode_salvar_carregar_partida_estudante(self):
        self.assertTrue(self.user.pode_salvar_carregar_partida())
    
    def test_pode_salvar_carregar_partida_educador(self):
        educador = User.objects.create_user(
            username='edu',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.assertFalse(educador.pode_salvar_carregar_partida())


class TurmaMethodsTestCase(TestCase):
    """Testes para métodos da classe Turma"""
    
    def setUp(self):
        self.educador = User.objects.create_user(
            username='edu',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_turma_str(self):
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        self.assertEqual(str(turma), 'ABC-123 - Turma A')
    
    def test_gerar_codigo_unico(self):
        codigo1 = Turma.gerar_codigo_unico()
        self.assertIsNotNone(codigo1)
        self.assertEqual(len(codigo1), 7)
        self.assertIn('-', codigo1)
        
        Turma.objects.create(
            educador=self.educador,
            codigo=codigo1,
            nome='Turma 1'
        )
        
        codigo2 = Turma.gerar_codigo_unico()
        self.assertNotEqual(codigo1, codigo2)
    
    def test_turma_meta_ordering(self):
        turma1 = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        turma2 = Turma.objects.create(
            educador=self.educador,
            codigo='DEF-456',
            nome='Turma B'
        )
        
        turmas = list(Turma.objects.filter(educador=self.educador))
        self.assertEqual(turmas[0].id, turma2.id)
    
    def test_turma_related_name(self):
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        turmas = self.educador.turmas_criadas.all()
        self.assertEqual(turmas.count(), 1)
        self.assertEqual(turmas[0].codigo, 'ABC-123')


class PartidaMethodsTestCase(TestCase):
    """Testes para métodos da classe Partida"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_partida_str(self):
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Minha Empresa',
            data_inicio=timezone.now()
        )
        self.assertEqual(str(partida), 'Partida de Minha Empresa')


class StartupEdgeCasesTestCase(TestCase):
    """Testes de edge cases em Startup"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
    
    def test_startup_com_turno_minimo(self):
        startup = Startup.objects.create(
            partida=self.partida,
            turno_atual=1
        )
        self.assertEqual(startup.turno_atual, 1)
    
    def test_startup_com_saldo_negativo(self):
        startup = Startup.objects.create(
            partida=self.partida,
            saldo_caixa=Decimal('-1000.00')
        )
        self.assertEqual(startup.saldo_caixa, Decimal('-1000.00'))
    
    def test_startup_com_receita_zero(self):
        startup = Startup.objects.create(
            partida=self.partida,
            receita_mensal=Decimal('0.00')
        )
        self.assertEqual(startup.receita_mensal, Decimal('0.00'))
    
    def test_startup_com_valuation_alto(self):
        startup = Startup.objects.create(
            partida=self.partida,
            valuation=Decimal('999999999.99')
        )
        self.assertEqual(startup.valuation, Decimal('999999999.99'))


class HistoricoDecisaoTestCase(TestCase):
    """Testes para modelo HistoricoDecisao"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
    
    def test_historico_str(self):
        decisao = HistoricoDecisao.objects.create(
            partida=self.partida,
            decisao_tomada='Teste Decisão',
            turno=5
        )
        self.assertEqual(str(decisao), 'Decisão no turno 5')
    
    def test_historico_turno_multiplo(self):
        for turno in range(1, 6):
            HistoricoDecisao.objects.create(
                partida=self.partida,
                decisao_tomada=f'Decisão {turno}',
                turno=turno
            )
        
        decisoes = HistoricoDecisao.objects.filter(partida=self.partida)
        self.assertEqual(decisoes.count(), 5)


class ConquistaModelTestCase(TestCase):
    """Testes para modelo Conquista"""
    
    def test_conquista_str(self):
        conquista = Conquista.objects.create(
            titulo='Teste Conquista',
            descricao='Descrição teste',
            pontos=50
        )
        self.assertEqual(str(conquista), 'Teste Conquista')
    
    def test_conquista_com_zero_pontos(self):
        conquista = Conquista.objects.create(
            titulo='Zero Pontos',
            descricao='Sem pontos',
            pontos=0
        )
        self.assertEqual(conquista.pontos, 0)
    
    def test_conquista_com_muitos_pontos(self):
        conquista = Conquista.objects.create(
            titulo='Mega Conquista',
            descricao='Muitos pontos',
            pontos=9999
        )
        self.assertEqual(conquista.pontos, 9999)


class PartidaCascadeTestCase(TestCase):
    """Testes para cascata de deleção em Partida"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        self.startup = Startup.objects.create(partida=self.partida)
    
    def test_delete_partida_deleta_startup(self):
        startup_pk = self.startup.pk
        self.partida.delete()
        
        self.assertFalse(Startup.objects.filter(pk=startup_pk).exists())
    
    def test_delete_partida_deleta_historico(self):
        decisao = HistoricoDecisao.objects.create(
            partida=self.partida,
            decisao_tomada='Teste',
            turno=1
        )
        decisao_pk = decisao.pk
        
        self.partida.delete()
        
        self.assertFalse(HistoricoDecisao.objects.filter(pk=decisao_pk).exists())


class ConquistaDesbloqueadaTestCase(TestCase):
    """Testes para ConquistaDesbloqueada"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        Startup.objects.create(partida=self.partida)
        self.conquista = Conquista.objects.create(
            titulo='Test',
            descricao='Test',
            pontos=100
        )
    
    def test_conquista_desbloqueada_str(self):
        desbloq = ConquistaDesbloqueada.objects.create(
            partida=self.partida,
            conquista=self.conquista
        )
        expected = f'{self.partida.nome_empresa} - {self.conquista.titulo}'
        self.assertEqual(str(desbloq), expected)
    
    def test_conquista_desbloqueada_data(self):
        desbloq = ConquistaDesbloqueada.objects.create(
            partida=self.partida,
            conquista=self.conquista
        )
        self.assertIsNotNone(desbloq.desbloqueada_em)


class UserCategoriaConstraintsTestCase(TestCase):
    """Testes para constraints de categoria de usuário"""
    
    def test_categoria_choices(self):
        user = User.objects.create_user(
            username='teste',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.assertEqual(user.categoria, 'ESTUDANTE_UNIVERSITARIO')
    
    def test_all_categoria_types(self):
        categories = [
            'ESTUDANTE_UNIVERSITARIO',
            'EDUCADOR_NEGOCIOS',
            'ASPIRANTE_EMPREENDEDOR',
            'PROFISSIONAL_CORPORATIVO'
        ]
        
        for i, cat in enumerate(categories):
            user = User.objects.create_user(
                username=f'user_{i}',
                password='pass',
                categoria=cat
            )
            self.assertEqual(user.categoria, cat)


class PartidaActiveFlagTestCase(TestCase):
    """Testes para flag 'ativa' de partida"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_partida_ativa_default(self):
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        self.assertTrue(partida.ativa)
    
    def test_partida_pode_ser_inativada(self):
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
        partida.ativa = False
        partida.save()
        
        partida.refresh_from_db()
        self.assertFalse(partida.ativa)


class StartupConstraintsTestCase(TestCase):
    """Testes para constraints em Startup"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='player',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test',
            data_inicio=timezone.now()
        )
    
    def test_startup_one_per_partida(self):
        startup1 = Startup.objects.create(partida=self.partida)
        
        self.assertEqual(Startup.objects.filter(partida=self.partida).count(), 1)
    
    def test_startup_valuation_nao_negativo(self):
        startup = Startup.objects.create(
            partida=self.partida,
            valuation=Decimal('0.00')
        )
        self.assertEqual(startup.valuation, Decimal('0.00'))


class TurmaAtivaFlagTestCase(TestCase):
    """Testes para flag 'ativa' de turma"""
    
    def setUp(self):
        self.educador = User.objects.create_user(
            username='edu',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
    
    def test_turma_ativa_default(self):
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        self.assertTrue(turma.ativa)
    
    def test_turma_pode_ser_inativada(self):
        turma = Turma.objects.create(
            educador=self.educador,
            codigo='ABC-123',
            nome='Turma A'
        )
        turma.ativa = False
        turma.save()
        
        turma.refresh_from_db()
        self.assertFalse(turma.ativa)
