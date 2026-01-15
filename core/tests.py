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
		Startup.objects.create(partida=self.partida, saldo_caixa=0000)

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

	def test_mensagem_ao_contratar_engenheiro_e_exibida_imediatamente(self):
		from decimal import Decimal
		from django.urls import reverse
		# Preparar partida e startup com caixa suficiente
		partida = Partida.objects.create(usuario=self.user, nome_empresa="HireTest")
		Startup.objects.create(partida=partida, saldo_caixa=Decimal('100000.00'), receita_mensal=Decimal('0.00'), valuation=Decimal('0.00'), funcionarios=0)

		# Login e ação
		self.client.login(username="tester", password="pass1234")
		response = self.client.post(reverse('salvar_jogo', args=[partida.id]), data={'decisao': 'Contratar Engenheiro Sênior'}, follow=True)

		# A mensagem deve aparecer no conteúdo renderizado da página final
		self.assertContains(response, '👨‍💻 Engenheiro contratado! Valuation aumentado.')

	def test_registro_exibe_mensagem_de_sucesso(self):
		from django.urls import reverse
		# Submeter formulário de registro
		response = self.client.post(reverse('registro'), data={
			'username': 'newuser',
			'email': 'newuser@example.com',
			'password1': 'novaSenha123',
			'password2': 'novaSenha123'
		}, follow=True)

		self.assertContains(response, 'Conta criada com sucesso!')

	def test_persistente_desbloqueada_apos_5_turnos(self):
		from core.services.conquistas import verificar_conquistas_progesso
		from core.models import ConquistaDesbloqueada
		from decimal import Decimal

		# Preparar partida com 5 turnos
		partida = Partida.objects.create(usuario=self.user, nome_empresa="PersistTest")
		Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000.00'), turno_atual=5)

		# Executar verificação de conquistas de progresso
		verificar_conquistas_progesso(self.user)

		# A conquista Persistente! deve existir para esta partida
		self.assertTrue(
			ConquistaDesbloqueada.objects.filter(partida=partida, conquista__titulo='Persistente!').exists()
		)

	def test_persistente_nao_desbloqueia_antes_de_5_turnos(self):
		from core.services.conquistas import verificar_conquistas_progesso
		from core.models import ConquistaDesbloqueada
		from decimal import Decimal

		# Preparar partida com 4 turnos
		partida = Partida.objects.create(usuario=self.user, nome_empresa="PersistTest2")
		Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000.00'), turno_atual=4)

		# Executar verificação
		verificar_conquistas_progesso(self.user)

		# A conquista não deve ter sido criada
		self.assertFalse(
			ConquistaDesbloqueada.objects.filter(partida=partida, conquista__titulo='Persistente!').exists()
		)
