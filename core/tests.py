from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Prefetch

from core.models import Partida, Startup, HistoricoDecisao


class ORMOptimizationTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="tester", email="t@example.com", password="pass1234"
		)
		# Outra conta para "ruído"
		other = User.objects.create_user(
			username="other", email="o@example.com", password="pass1234"
		)

		# Partida do usuário principal
		self.partida = Partida.objects.create(usuario=self.user, nome_empresa="ACME")
		Startup.objects.create(partida=self.partida, saldo_caixa=10000)

		# Histórico da partida principal
		HistoricoDecisao.objects.bulk_create(
			[
				HistoricoDecisao(partida=self.partida, decisao_tomada=f"D{i}", turno=i)
				for i in range(1, 11)
			]
		)

		# Dados de outra partida/usuário
		p2 = Partida.objects.create(usuario=other, nome_empresa="OtherCo")
		Startup.objects.create(partida=p2, saldo_caixa=5000)
		HistoricoDecisao.objects.create(partida=p2, decisao_tomada="X", turno=1)

	def test_carregar_jogo_queryset_prefetch_select_related(self):
		# 1 query para Partida+Startup (select_related) + 1 query para prefetch de decisões
		with self.assertNumQueries(2):
			p = (
				Partida.objects.select_related("startup").prefetch_related(
					Prefetch(
						"decisoes",
						queryset=HistoricoDecisao.objects.order_by("turno"),
					)
				)
				.filter(usuario=self.user)
				.get(id=self.partida.id)
			)

			_ = p.startup.saldo_caixa  # não deve gerar query extra
			_ = list(p.decisoes.all())  # já deve estar em cache pelo prefetch

	def test_historico_queryset_select_related(self):
		# 1 query para obter todas as decisões (com join em partida),
		# iterar e acessar p.nome_empresa não deve gerar queries extras
		qs = (
			HistoricoDecisao.objects.select_related("partida")
			.filter(partida__usuario=self.user)
			.order_by("-data_decisao")
		)

		with self.assertNumQueries(1):
			rows = list(qs)
			_ = [r.partida.nome_empresa for r in rows]

	def test_metricas_queryset_select_related(self):
		# 1 query para partida+startup via select_related
		with self.assertNumQueries(1):
			p = (
				Partida.objects.select_related("startup")
				.filter(usuario=self.user)
				.get(id=self.partida.id)
			)
			_ = p.startup.turno_atual

	def test_dashboard_queryset_index_usage_smoke(self):
		# Smoke: apenas garante 1 query na listagem do dashboard
		with self.assertNumQueries(1):
			rows = list(
				Partida.objects.filter(usuario=self.user).order_by("-data_inicio")
			)
			self.assertTrue(len(rows) >= 1)
