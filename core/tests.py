from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    Conquista,
    ConquistaDesbloqueada,
    Evento,
    EventoPartida,
    Fundador,
    HistoricoDecisao,
    Partida,
    Startup,
)


class PartidaTestCase(TestCase):
    """Testes para o modelo Partida"""

    def setUp(self):
        """Cria usuário e partida para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")

    def test_partida_creation(self):
        """Testa criação básica de partida"""
        self.assertEqual(self.partida.nome_empresa, "Tech Startup")
        self.assertEqual(self.partida.usuario, self.usuario)

    def test_partida_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.partida), "Partida de Tech Startup")

    def test_partida_ordering(self):
        """Testa ordenação das partidas (mais recentes primeiro)"""
        partida2 = Partida.objects.create(usuario=self.usuario, nome_empresa="Second Startup")
        partidas = Partida.objects.all()
        self.assertEqual(partidas.first(), partida2)  # Mais recente deve ser primeiro


class StartupTestCase(TestCase):
    """Testes para o modelo Startup"""

    def setUp(self):
        """Cria partida e startup para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.startup = Startup.objects.create(
            partida=self.partida,
            saldo_caixa=Decimal("10000.00"),
            receita_mensal=Decimal("1000.00"),
            valuation=Decimal("50000.00"),
            funcionarios=5,
        )

    def test_startup_creation(self):
        """Testa criação de startup com valores iniciais"""
        self.assertEqual(self.startup.saldo_caixa, Decimal("10000.00"))
        self.assertEqual(self.startup.turno_atual, 1)
        self.assertEqual(self.startup.funcionarios, 5)

    def test_startup_defaults(self):
        """Testa valores padrão da startup"""
        partida2 = Partida.objects.create(usuario=self.usuario, nome_empresa="Second Startup")
        startup2 = Startup.objects.create(partida=partida2)
        self.assertEqual(startup2.saldo_caixa, Decimal("10000.00"))
        self.assertEqual(startup2.funcionarios, 1)

    def test_startup_one_to_one_relationship(self):
        """Testa relação 1:1 entre Partida e Startup"""
        self.assertEqual(self.partida.startup, self.startup)

    def test_startup_str_representation(self):
        """Testa representação em string"""
        self.startup.nome = "Minha Empresa"
        self.startup.save()
        self.assertEqual(str(self.startup), "Minha Empresa")


class HistoricoDecisaoTestCase(TestCase):
    """Testes para o modelo HistoricoDecisao"""

    def setUp(self):
        """Cria partida e histórico para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.decisao = HistoricoDecisao.objects.create(
            partida=self.partida, decisao_tomada="Investir em marketing", turno=1
        )

    def test_historico_creation(self):
        """Testa criação de decisão no histórico"""
        self.assertEqual(self.decisao.decisao_tomada, "Investir em marketing")
        self.assertEqual(self.decisao.turno, 1)

    def test_historico_ordering(self):
        """Testa ordenação por turno"""
        decisao2 = HistoricoDecisao.objects.create(
            partida=self.partida, decisao_tomada="Contratar engenheiro", turno=2
        )
        decisoes = HistoricoDecisao.objects.filter(partida=self.partida)
        self.assertEqual(list(decisoes), [self.decisao, decisao2])

    def test_historico_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.decisao), "Decisão no turno 1")


class FundadorTestCase(TestCase):
    """Testes para o modelo Fundador"""

    def setUp(self):
        """Cria partida e fundador para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.fundador = Fundador.objects.create(
            partida=self.partida,
            nome="João Silva",
            idade=28,
            experiencia=Fundador.Experiencia.TECNOLOGIA,
            anos_experiencia=5,
        )

    def test_fundador_creation(self):
        """Testa criação de fundador"""
        self.assertEqual(self.fundador.nome, "João Silva")
        self.assertEqual(self.fundador.idade, 28)
        self.assertEqual(self.fundador.anos_experiencia, 5)

    def test_fundador_experiencia_choices(self):
        """Testa escolhas de experiência disponíveis"""
        self.assertEqual(self.fundador.experiencia, Fundador.Experiencia.TECNOLOGIA)
        self.fundador.experiencia = Fundador.Experiencia.NEGOCIOS
        self.fundador.save()
        self.fundador.refresh_from_db()
        self.assertEqual(self.fundador.experiencia, Fundador.Experiencia.NEGOCIOS)

    def test_fundador_idade_validator(self):
        """Testa validação de idade mínima (16 anos)"""
        fundador_young = Fundador(
            partida=self.partida, nome="Young", idade=15, experiencia=Fundador.Experiencia.PRODUTO
        )
        with self.assertRaises(ValidationError):
            fundador_young.full_clean()

    def test_fundador_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.fundador), "João Silva (Tecnologia)")

    def test_fundador_one_to_one_relationship(self):
        """Testa relação 1:1 entre Partida e Fundador"""
        self.assertEqual(self.partida.fundador, self.fundador)


class EventoTestCase(TestCase):
    """Testes para o modelo Evento"""

    def setUp(self):
        """Cria evento para os testes"""
        self.evento = Evento.objects.create(
            titulo="Novo Concorrente",
            descricao="Um concorrente forte entrou no mercado",
            categoria=Evento.Categoria.MERCADO,
            chance_base=Decimal("0.25"),
            impacto_saldo=Decimal("-5000.00"),
            impacto_receita=Decimal("-500.00"),
            turno_minimo=3,
        )

    def test_evento_creation(self):
        """Testa criação de evento"""
        self.assertEqual(self.evento.titulo, "Novo Concorrente")
        self.assertEqual(self.evento.categoria, Evento.Categoria.MERCADO)

    def test_evento_chance_base_validator(self):
        """Testa validação de chance_base entre 0 e 1"""
        evento_invalid = Evento(
            titulo="Teste", categoria=Evento.Categoria.MERCADO, chance_base=Decimal("1.5")
        )
        with self.assertRaises(ValidationError):
            evento_invalid.full_clean()

    def test_evento_ativo_default(self):
        """Testa que evento é ativo por padrão"""
        self.assertTrue(self.evento.ativo)

    def test_evento_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.evento), "Novo Concorrente")


class EventoPartidaTestCase(TestCase):
    """Testes para o modelo EventoPartida"""

    def setUp(self):
        """Cria partida, evento e ocorrência para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.evento = Evento.objects.create(
            titulo="Novo Concorrente",
            categoria=Evento.Categoria.MERCADO,
            chance_base=Decimal("0.25"),
        )
        self.evento_partida = EventoPartida.objects.create(
            partida=self.partida, evento=self.evento, turno=5
        )

    def test_evento_partida_creation(self):
        """Testa criação de ocorrência de evento"""
        self.assertEqual(self.evento_partida.turno, 5)
        self.assertFalse(self.evento_partida.resolvido)

    def test_evento_partida_unique_constraint(self):
        """Testa constraint de unicidade por partida/evento/turno"""
        with self.assertRaises(Exception):  # IntegrityError
            EventoPartida.objects.create(partida=self.partida, evento=self.evento, turno=5)

    def test_evento_partida_resolve(self):
        """Testa marcação como resolvido"""
        self.evento_partida.resolvido = True
        self.evento_partida.resultado = "Competição aumentou em 30%"
        self.evento_partida.save()
        self.evento_partida.refresh_from_db()
        self.assertTrue(self.evento_partida.resolvido)

    def test_evento_partida_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.evento_partida), "Novo Concorrente (T5)")


class ConquistaTestCase(TestCase):
    """Testes para o modelo Conquista"""

    def setUp(self):
        """Cria conquista para os testes"""
        self.conquista = Conquista.objects.create(
            titulo="Primeira Venda",
            descricao="Realize sua primeira venda",
            tipo=Conquista.Tipo.FINANCEIRO,
            valor_objetivo=Decimal("1000.00"),
            pontos=50,
        )

    def test_conquista_creation(self):
        """Testa criação de conquista"""
        self.assertEqual(self.conquista.titulo, "Primeira Venda")
        self.assertEqual(self.conquista.pontos, 50)
        self.assertTrue(self.conquista.ativo)

    def test_conquista_tipos_choices(self):
        """Testa tipos de conquista disponíveis"""
        self.assertEqual(self.conquista.tipo, Conquista.Tipo.FINANCEIRO)
        conquista2 = Conquista.objects.create(
            titulo="Crescimento", tipo=Conquista.Tipo.PROGRESSO
        )
        self.assertEqual(conquista2.tipo, Conquista.Tipo.PROGRESSO)

    def test_conquista_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(str(self.conquista), "Primeira Venda")


class ConquistaDesbloqueadaTestCase(TestCase):
    """Testes para o modelo ConquistaDesbloqueada"""

    def setUp(self):
        """Cria partida, conquista e desbloqueio para os testes"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.conquista = Conquista.objects.create(
            titulo="Primeira Venda", tipo=Conquista.Tipo.FINANCEIRO
        )
        self.desbloqueio = ConquistaDesbloqueada.objects.create(
            partida=self.partida, conquista=self.conquista, turno=10
        )

    def test_conquista_desbloqueada_creation(self):
        """Testa criação de desbloqueio"""
        self.assertEqual(self.desbloqueio.turno, 10)
        self.assertEqual(self.desbloqueio.conquista, self.conquista)

    def test_conquista_desbloqueada_unique_constraint(self):
        """Testa constraint de unicidade por partida/conquista"""
        with self.assertRaises(Exception):  # IntegrityError
            ConquistaDesbloqueada.objects.create(
                partida=self.partida, conquista=self.conquista, turno=11
            )

    def test_conquista_desbloqueada_str_representation(self):
        """Testa representação em string"""
        self.assertEqual(
            str(self.desbloqueio), "Primeira Venda - Tech Startup"
        )

    def test_conquista_desbloqueada_ordering(self):
        """Testa ordenação por data de desbloqueio (mais recente primeiro)"""
        conquista2 = Conquista.objects.create(
            titulo="Segunda Conquista", tipo=Conquista.Tipo.OPERACIONAL
        )
        desbloqueio2 = ConquistaDesbloqueada.objects.create(
            partida=self.partida, conquista=conquista2, turno=15
        )
        desbloqueios = ConquistaDesbloqueada.objects.filter(partida=self.partida)
        self.assertEqual(desbloqueios.first(), desbloqueio2)  # Mais recente primeiro


class IntegrationTestCase(TestCase):
    """Testes de integração entre os modelos"""

    def setUp(self):
        """Cria estrutura completa para testes de integração"""
        self.usuario = User.objects.create_user(username="testuser", password="pass123")
        self.partida = Partida.objects.create(usuario=self.usuario, nome_empresa="Tech Startup")
        self.startup = Startup.objects.create(partida=self.partida)
        self.fundador = Fundador.objects.create(
            partida=self.partida,
            nome="João Silva",
            experiencia=Fundador.Experiencia.TECNOLOGIA,
        )

    def test_partida_cascade_delete(self):
        """Testa que deletar partida deleta startup relacionada"""
        startup_id = self.startup.id
        self.partida.delete()
        self.assertFalse(Startup.objects.filter(id=startup_id).exists())

    def test_full_game_flow(self):
        """Testa fluxo completo: partida -> startup -> decisão -> evento -> conquista"""
        # Simula decisão no turno 1
        decisao = HistoricoDecisao.objects.create(
            partida=self.partida, decisao_tomada="Investir em marketing", turno=1
        )

        # Cria evento possível
        evento = Evento.objects.create(
            titulo="Novo Concorrente",
            categoria=Evento.Categoria.MERCADO,
            chance_base=Decimal("0.5"),
            impacto_saldo=Decimal("-1000.00"),
        )

        # Evento ocorre no turno 2
        evento_partida = EventoPartida.objects.create(
            partida=self.partida, evento=evento, turno=2
        )

        # Conquista é desbloqueada no turno 3
        conquista = Conquista.objects.create(
            titulo="Sobrevivi ao Concorrente", tipo=Conquista.Tipo.PROGRESSO, pontos=25
        )
        desbloqueio = ConquistaDesbloqueada.objects.create(
            partida=self.partida, conquista=conquista, turno=3
        )

        # Verificações
        self.assertEqual(self.partida.decisoes.count(), 1)
        self.assertEqual(self.partida.eventos.count(), 1)
        self.assertEqual(self.partida.conquistas.count(), 1)

    def test_related_manager_access(self):
        """Testa acesso via related_name aos objetos relacionados"""
        # Partida pode acessar sua startup, fundador, decisões, eventos, conquistas
        self.assertIsNotNone(self.partida.startup)
        self.assertIsNotNone(self.partida.fundador)
        self.assertEqual(self.partida.decisoes.count(), 0)
        self.assertEqual(self.partida.eventos.count(), 0)
        self.assertEqual(self.partida.conquistas.count(), 0)
