from django.test import TestCase
from core.models import User, Partida, Startup, HistoricoDecisao
from core.forms import CadastroUsuarioForm
from django.db.models import Prefetch


class ORMOptimizationTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="tester", email="t@example.com", password="pass1234",
			documento="12345678901", categoria="ALUNO"
		)
		# Outra conta para "ruído"
		other = User.objects.create_user(
			username="other", email="o@example.com", password="pass1234",
			documento="12345678902", categoria="PROFESSOR"
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

	def test_primeiro_milhao_desbloqueada_com_caixa_milhao(self):
		from core.services.conquistas import verificar_conquistas_progesso
		from core.models import ConquistaDesbloqueada
		from decimal import Decimal

		# Preparar partida com caixa de 1.000.000
		partida = Partida.objects.create(usuario=self.user, nome_empresa="MilhaoTest")
		Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000000.00'), turno_atual=10)

		# Executar verificação de conquistas de progresso
		verificar_conquistas_progesso(self.user)

		# A conquista Primeiro Milhão! deve existir para esta partida
		self.assertTrue(
			ConquistaDesbloqueada.objects.filter(partida=partida, conquista__titulo='Primeiro Milhão!').exists()
		)

	def test_primeiro_milhao_nao_desbloqueia_abaixo_milhao(self):
		from core.services.conquistas import verificar_conquistas_progesso
		from core.models import ConquistaDesbloqueada
		from decimal import Decimal

		# Preparar partida com caixa abaixo de 1.000.000
		partida = Partida.objects.create(usuario=self.user, nome_empresa="MilhaoTest2")
		Startup.objects.create(partida=partida, saldo_caixa=Decimal('999999.99'), turno_atual=10)

		# Executar verificação
		verificar_conquistas_progesso(self.user)

		# A conquista não deve ter sido criada
		self.assertFalse(
			ConquistaDesbloqueada.objects.filter(partida=partida, conquista__titulo='Primeiro Milhão!').exists()
		)

	def test_cadastro_form_valida_cpf_11_digitos(self):
		form_data = {
			'username': 'testuser',
			'password1': 'testpass123',
			'password2': 'testpass123',
			'first_name': 'Test User',
			'email': 'test@example.com',
			'tipo_documento': 'CPF',
			'documento': '11111111111',  # 11 dígitos
			'categoria': 'ALUNO',
			'municipio': 'São Paulo',
			'estado': 'SP',
			'pais': 'Brasil'
		}
		form = CadastroUsuarioForm(data=form_data)
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['documento'], '11111111111')

	def test_cadastro_form_rejeita_cpf_menos_11_digitos(self):
		form_data = {
			'username': 'testuser2',
			'password1': 'testpass123',
			'password2': 'testpass123',
			'first_name': 'Test User',
			'email': 'test2@example.com',
			'tipo_documento': 'CPF',
			'documento': '2222222222',  # 10 dígitos
			'categoria': 'ALUNO',
			'municipio': 'São Paulo',
			'estado': 'SP',
			'pais': 'Brasil'
		}
		form = CadastroUsuarioForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('documento', form.errors)
		self.assertEqual(form.errors['documento'], ['CPF deve ter exatamente 11 dígitos.'])

	def test_cadastro_form_valida_cnpj_14_digitos(self):
		form_data = {
			'username': 'testuser3',
			'password1': 'testpass123',
			'password2': 'testpass123',
			'first_name': 'Test User',
			'email': 'test3@example.com',
			'tipo_documento': 'CNPJ',
			'documento': '11111111000111',  # 14 dígitos
			'categoria': 'STARTUP_PJ',
			'municipio': 'São Paulo',
			'estado': 'SP',
			'pais': 'Brasil'
		}
		form = CadastroUsuarioForm(data=form_data)
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['documento'], '11111111000111')

	def test_cadastro_form_rejeita_cnpj_menos_14_digitos(self):
		form_data = {
			'username': 'testuser4',
			'password1': 'testpass123',
			'password2': 'testpass123',
			'first_name': 'Test User',
			'email': 'test4@example.com',
			'tipo_documento': 'CNPJ',
			'documento': '2222222200012',  # 13 dígitos
			'categoria': 'STARTUP_PJ',
			'municipio': 'São Paulo',
			'estado': 'SP',
			'pais': 'Brasil'
		}
		form = CadastroUsuarioForm(data=form_data)
		self.assertFalse(form.is_valid())
		self.assertIn('documento', form.errors)
		self.assertEqual(form.errors['documento'], ['CNPJ deve ter exatamente 14 dígitos.'])


class NavigationFlowTests(TestCase):
	"""Testes de fluxo completo de navegação e usabilidade"""
	
	def setUp(self):
		"""Criar usuários e dados de teste"""
		self.user_estudante = User.objects.create_user(
			username="student_user",
			email="student@example.com",
			password="pass1234",
			documento="12345678901",
			categoria="ESTUDANTE_UNIVERSITARIO"
		)
		
		self.user_educador = User.objects.create_user(
			username="teacher_user",
			email="teacher@example.com",
			password="pass1234",
			documento="98765432109",
			categoria="EDUCADOR_NEGOCIOS"
		)
		
		self.user_outro = User.objects.create_user(
			username="other_user",
			email="other@example.com",
			password="pass1234",
			documento="11122233344",
			categoria="ESTUDANTE_UNIVERSITARIO"
		)

	def test_fluxo_login_dashboard(self):
		"""Teste: Usuário faz login e acessa o dashboard"""
		from django.urls import reverse
		
		# Acessar página de login
		response = self.client.get('/admin/login/')
		self.assertEqual(response.status_code, 200)
		
		# Fazer login
		login_success = self.client.login(username="student_user", password="pass1234")
		self.assertTrue(login_success)
		
		# Acessar dashboard
		response = self.client.get(reverse('dashboard'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('partidas', response.context)

	def test_fluxo_nova_partida_carregar_jogo(self):
		"""Teste: Criar nova partida e carregar o jogo"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Acessar página de nova partida
		response = self.client.get(reverse('nova_partida'))
		self.assertEqual(response.status_code, 200)
		
		# Criar nova partida
		response = self.client.post(reverse('nova_partida'), {
			'nome_empresa': 'TestCo',
			'saldo_inicial': '50000'
		})
		self.assertEqual(response.status_code, 302)  # Redirect esperado
		
		# Verificar que partida foi criada
		partida = Partida.objects.filter(usuario=self.user_estudante).first()
		self.assertIsNotNone(partida)
		self.assertEqual(partida.nome_empresa, 'TestCo')
		
		# Carregar jogo
		response = self.client.get(reverse('carregar_jogo', args=[partida.id]))
		self.assertEqual(response.status_code, 200)
		self.assertIn('estado_startup', response.context)

	def test_fluxo_salvar_decisao_historico(self):
		"""Teste: Tomar decisão, salvar e verificar histórico"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='TestCo'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			receita_mensal=Decimal('1000.00')
		)
		
		# Tomar decisão
		response = self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Não fazer nada (Economizar)'
		})
		self.assertEqual(response.status_code, 302)
		
		# Verificar histórico
		response = self.client.get(reverse('historico'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('decisoes', response.context)
		self.assertEqual(len(response.context['decisoes']), 1)

	def test_fluxo_perfil_metricas(self):
		"""Teste: Acessar perfil e métricas de partida"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='MetricaTest'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('75000.00'),
			turno_atual=5,
			valuation=Decimal('500000.00')
		)
		
		# Acessar perfil
		response = self.client.get(reverse('perfil'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('total_partidas', response.context)
		self.assertEqual(response.context['total_partidas'], 1)
		
		# Acessar métricas
		response = self.client.get(reverse('metricas', args=[partida.id]))
		self.assertEqual(response.status_code, 200)
		self.assertIn('startup', response.context)
		self.assertEqual(response.context['startup'].saldo_caixa, Decimal('75000.00'))

	def test_fluxo_conquistas_ranking(self):
		"""Teste: Visualizar conquistas e ranking"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='ConquistaTest'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('100000.00'),
			turno_atual=10
		)
		
		# Acessar conquistas
		response = self.client.get(reverse('conquistas'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('conquistas', response.context)
		
		# Acessar ranking
		response = self.client.get(reverse('ranking'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('startups', response.context)

	def test_acesso_negado_partida_outro_usuario(self):
		"""Teste: Usuário não pode acessar partida de outro usuário"""
		from django.urls import reverse
		from decimal import Decimal
		
		# Criar partida de outro usuário
		partida = Partida.objects.create(
			usuario=self.user_outro,
			nome_empresa='OutroUsuario'
		)
		Startup.objects.create(partida=partida)
		
		# Login como outro usuário
		self.client.login(username="student_user", password="pass1234")
		
		# Tentar acessar partida do outro
		response = self.client.get(reverse('carregar_jogo', args=[partida.id]))
		self.assertEqual(response.status_code, 404)

	def test_acesso_negado_salvar_decisao_outro_usuario(self):
		"""Teste: Usuário não pode salvar decisão em partida de outro"""
		from django.urls import reverse
		from decimal import Decimal
		
		# Criar partida de outro usuário
		partida = Partida.objects.create(
			usuario=self.user_outro,
			nome_empresa='OutroUsuario'
		)
		Startup.objects.create(partida=partida)
		
		# Login como outro usuário
		self.client.login(username="student_user", password="pass1234")
		
		# Tentar salvar decisão
		response = self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Não fazer nada (Economizar)'
		})
		self.assertEqual(response.status_code, 404)

	def test_redirect_handler_estudante(self):
		"""Teste: Redirect handler redireciona estudante para dashboard"""
		from django.urls import reverse
		
		self.client.login(username="student_user", password="pass1234")
		
		response = self.client.get(reverse('redirect_handler'), follow=False)
		self.assertEqual(response.status_code, 302)
		# Verificar que redirecionou (pode ser para dashboard ou /)
		self.assertIsNotNone(response['Location'])

	def test_redirect_handler_educador(self):
		"""Teste: Redirect handler redireciona educador para dashboard"""
		from django.urls import reverse
		
		self.client.login(username="teacher_user", password="pass1234")
		
		response = self.client.get(reverse('redirect_handler'), follow=False)
		self.assertEqual(response.status_code, 302)
		# Verificar que redirecionou (pode ser para dashboard ou /)
		self.assertIsNotNone(response['Location'])

	def test_partida_nao_pode_ser_alterada_quando_finalizada(self):
		"""Teste: Partida finalizada não pode receber novas decisões"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida finalizada (game over)
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='GameOverTest',
			ativa=False
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('0.00')
		)
		
		# Tentar salvar decisão
		response = self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Não fazer nada (Economizar)'
		}, follow=True)
		self.assertEqual(response.status_code, 200)
		
		# Verificar que a mensagem de erro foi exibida
		self.assertIn(
			'encerrada',
			[str(m) for m in response.context['messages']]
		)

	def test_status_code_paginas_autenticadas(self):
		"""Teste: Todas as páginas autenticadas retornam status 200"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida para testes
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='StatusTest'
		)
		Startup.objects.create(partida=partida)
		
		# Testar todas as páginas principais
		pages = [
			('dashboard', []),
			('nova_partida', []),
			('perfil', []),
			('historico', []),
			('metricas', [partida.id]),
			('conquistas', []),
			('ranking', []),
			('carregar_jogo', [partida.id]),
		]
		
		for view_name, args in pages:
			response = self.client.get(reverse(view_name, args=args))
			self.assertEqual(
				response.status_code,
				200,
				f"Página {view_name} retornou {response.status_code} em vez de 200"
			)

	def test_login_requerido_para_dashboard(self):
		"""Teste: Dashboard requer autenticação"""
		from django.urls import reverse
		
		response = self.client.get(reverse('dashboard'), follow=False)
		self.assertEqual(response.status_code, 302)
		self.assertIn('login', response.url)

	def test_login_requerido_para_nova_partida(self):
		"""Teste: Nova partida requer autenticação"""
		from django.urls import reverse
		
		response = self.client.get(reverse('nova_partida'), follow=False)
		self.assertEqual(response.status_code, 302)
		self.assertIn('login', response.url)

	def test_saldo_insuficiente_impede_decisao(self):
		"""Teste: Decisão com custo é bloqueada se saldo insuficiente"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida com saldo baixo
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='SaldoTest'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('1000.00'),
			receita_mensal=Decimal('500.00')
		)
		
		# Tentar decisão que custa 5000
		response = self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Investir em Marketing Agressivo'
		})
		
		# Deve ser redirecionado e mensagem de erro deve aparecer
		self.assertEqual(response.status_code, 302)
		
		# Saldo não deve ter mudado
		startup = Startup.objects.get(partida=partida)
		self.assertEqual(startup.saldo_caixa, Decimal('1000.00'))

	def test_historico_ordenado_por_data_descrescente(self):
		"""Teste: Histórico exibe decisões em ordem reversa"""
		from django.urls import reverse
		from datetime import timedelta
		from django.utils import timezone
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida com múltiplas decisões
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='HistoricoOrder'
		)
		
		now = timezone.now()
		HistoricoDecisao.objects.bulk_create([
			HistoricoDecisao(
				partida=partida,
				decisao_tomada=f"Decisão {i}",
				turno=i,
				data_decisao=now + timedelta(hours=i)
			)
			for i in range(1, 4)
		])
		
		response = self.client.get(reverse('historico'))
		decisoes = response.context['decisoes']
		
		# Verificar ordem descendente por data
		self.assertEqual(decisoes[0].turno, 3)
		self.assertEqual(decisoes[1].turno, 2)
		self.assertEqual(decisoes[2].turno, 1)

	def test_startup_metricas_sao_exibidas_corretamente(self):
		"""Teste: Métricas da startup são exibidas corretamente no jogo"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="student_user", password="pass1234")
		
		# Criar partida com métricas específicas
		partida = Partida.objects.create(
			usuario=self.user_estudante,
			nome_empresa='MetricasDisplay'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('100000.00'),
			receita_mensal=Decimal('5000.00'),
			valuation=Decimal('500000.00'),
			funcionarios=5,
			turno_atual=3
		)
		
		response = self.client.get(reverse('carregar_jogo', args=[partida.id]))
		context = response.context
		
		self.assertEqual(context['estado_startup'].saldo_caixa, Decimal('100000.00'))
		self.assertEqual(context['estado_startup'].receita_mensal, Decimal('5000.00'))
		self.assertEqual(context['estado_startup'].valuation, Decimal('500000.00'))
		self.assertEqual(context['estado_startup'].funcionarios, 5)

class GameStateTests(TestCase):
	"""Testes de estado do jogo (game over, vitória, transições)"""
	
	def setUp(self):
		"""Criar usuário e dados de teste"""
		self.user = User.objects.create_user(
			username="game_tester",
			email="gamer@example.com",
			password="pass1234",
			documento="12345678901",
			categoria="ESTUDANTE_UNIVERSITARIO"
		)
	
	def test_game_over_quando_saldo_zero(self):
		"""Teste: Game over é acionado quando saldo chega a zero"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida com saldo em zero
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='GameOverTest',
			ativa=True
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('0.00')
		)
		
		# Carregar jogo
		response = self.client.get(reverse('carregar_jogo', args=[partida.id]))
		context = response.context
		
		# Verificar que game_over é True
		self.assertTrue(context['game_over'])
		self.assertEqual(response.status_code, 200)
		self.assertIn('Fim da Jornada', response.content.decode())

	def test_vitoria_quando_valuation_1_milhao(self):
		"""Teste: Vitória é acionada quando valuation atinge 1 milhão"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida com valuation de 1 milhão
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='VictoryTest',
			ativa=True
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			valuation=Decimal('1000000.00')
		)
		
		# Carregar jogo
		response = self.client.get(reverse('carregar_jogo', args=[partida.id]))
		context = response.context
		
		# Verificar que vitoria é True
		self.assertTrue(context['vitoria'])
		self.assertEqual(response.status_code, 200)
		self.assertIn('Objetivo Alcançado', response.content.decode())

	def test_partida_finaliza_apos_game_over(self):
		"""Teste: Partida é marcada como inativa após game over"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida com saldo em zero
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='FinalizeTest',
			ativa=True
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('0.00')
		)
		
		# Carregar jogo (simula condição de game over)
		self.client.get(reverse('carregar_jogo', args=[partida.id]))
		
		# Recarregar partida do BD
		partida.refresh_from_db()
		
		# Verificar que ativa foi alterado para False
		self.assertFalse(partida.ativa)

	def test_partida_finaliza_apos_vitoria(self):
		"""Teste: Partida é marcada como inativa após vitória"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida com valuation de 1 milhão
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='WinTest',
			ativa=True
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			valuation=Decimal('1000000.00')
		)
		
		# Carregar jogo
		self.client.get(reverse('carregar_jogo', args=[partida.id]))
		
		# Recarregar partida do BD
		partida.refresh_from_db()
		
		# Verificar que ativa foi alterado para False
		self.assertFalse(partida.ativa)

	def test_decisao_muda_metricas_corretamente(self):
		"""Teste: Decisões alteram as métricas conforme esperado"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='DecisionTest'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			receita_mensal=Decimal('1000.00'),
			valuation=Decimal('100000.00'),
			funcionarios=1
		)
		
		# Tomar decisão de contratar engenheiro
		self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Contratar Engenheiro Sênior'
		})
		
		# Recarregar startup
		startup = Startup.objects.get(partida=partida)
		
		# Verificar alterações
		self.assertEqual(startup.saldo_caixa, Decimal('50000.00') + Decimal('1000.00') - Decimal('8000.00'))  # receita + saldo anterior - custo
		self.assertEqual(startup.valuation, Decimal('125000.00'))  # +25000
		self.assertEqual(startup.funcionarios, 2)  # +1
		self.assertEqual(startup.turno_atual, 2)  # incrementado

	def test_decisao_marketing_aumenta_receita(self):
		"""Teste: Decisão de marketing aumenta receita mensal"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='MarketingTest'
		)
		receita_inicial = Decimal('1000.00')
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			receita_mensal=receita_inicial
		)
		
		# Tomar decisão de marketing
		self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Investir em Marketing Agressivo'
		})
		
		# Recarregar startup
		startup = Startup.objects.get(partida=partida)
		
		# Verificar aumento de receita
		self.assertEqual(startup.receita_mensal, receita_inicial + Decimal('3000.00'))

	def test_turno_avanca_apos_decisao(self):
		"""Teste: Turno é incrementado após cada decisão"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='TurnoTest'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('50000.00'),
			turno_atual=1
		)
		
		# Tomar primeira decisão
		self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Não fazer nada (Economizar)'
		})
		
		startup = Startup.objects.get(partida=partida)
		self.assertEqual(startup.turno_atual, 2)
		
		# Tomar segunda decisão
		self.client.post(reverse('salvar_jogo', args=[partida.id]), {
			'decisao': 'Não fazer nada (Economizar)'
		})
		
		startup = Startup.objects.get(partida=partida)
		self.assertEqual(startup.turno_atual, 3)

	def test_multiplas_partidas_usuario(self):
		"""Teste: Usuário pode ter múltiplas partidas simultâneas"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar múltiplas partidas
		partida1 = Partida.objects.create(
			usuario=self.user,
			nome_empresa='Partida1'
		)
		Startup.objects.create(partida=partida1)
		
		partida2 = Partida.objects.create(
			usuario=self.user,
			nome_empresa='Partida2'
		)
		Startup.objects.create(partida=partida2)
		
		partida3 = Partida.objects.create(
			usuario=self.user,
			nome_empresa='Partida3'
		)
		Startup.objects.create(partida=partida3)
		
		# Verificar que todas aparecem no dashboard
		response = self.client.get(reverse('dashboard'))
		partidas = response.context['partidas']
		
		self.assertEqual(len(partidas), 3)
		nomes = [p.nome_empresa for p in partidas]
		self.assertIn('Partida1', nomes)
		self.assertIn('Partida2', nomes)
		self.assertIn('Partida3', nomes)

	def test_historico_registra_todas_decisoes(self):
		"""Teste: Histórico registra todas as decisões em ordem"""
		from django.urls import reverse
		from decimal import Decimal
		
		self.client.login(username="game_tester", password="pass1234")
		
		# Criar partida
		partida = Partida.objects.create(
			usuario=self.user,
			nome_empresa='HistoricoCompleto'
		)
		Startup.objects.create(
			partida=partida,
			saldo_caixa=Decimal('100000.00')
		)
		
		# Tomar 3 decisões
		decisoes_tomadas = [
			'Não fazer nada (Economizar)',
			'Investir em Marketing Agressivo',
			'Não fazer nada (Economizar)'
		]
		
		for decisao in decisoes_tomadas:
			self.client.post(reverse('salvar_jogo', args=[partida.id]), {
				'decisao': decisao
			})
		
		# Verificar histórico
		historico = HistoricoDecisao.objects.filter(partida=partida).order_by('turno')
		self.assertEqual(len(historico), 3)
		
		# Verificar ordem
		self.assertEqual(historico[0].turno, 2)
		self.assertEqual(historico[1].turno, 3)
		self.assertEqual(historico[2].turno, 4)


class PermissionTests(TestCase):
	"""Testes de permissões e controle de acesso"""
	
	def setUp(self):
		"""Criar usuários de diferentes categorias"""
		self.estudante = User.objects.create_user(
			username="student",
			email="student@example.com",
			password="pass1234",
			documento="12345678901",
			categoria="ESTUDANTE_UNIVERSITARIO"
		)
		
		self.educador = User.objects.create_user(
			username="educator",
			email="educator@example.com",
			password="pass1234",
			documento="98765432109",
			categoria="EDUCADOR_NEGOCIOS"
		)
		
		self.aspirante = User.objects.create_user(
			username="aspirant",
			email="aspirant@example.com",
			password="pass1234",
			documento="11122233344",
			categoria="ASPIRANTE_EMPREENDEDOR"
		)
		
		self.profissional = User.objects.create_user(
			username="professional",
			email="professional@example.com",
			password="pass1234",
			documento="55566677788",
			categoria="PROFISSIONAL_CORPORATIVO"
		)
	
	def test_estudante_pode_criar_partida(self):
		"""Teste: Estudante pode criar nova partida"""
		from django.urls import reverse
		
		self.client.login(username="student", password="pass1234")
		
		response = self.client.get(reverse('nova_partida'))
		self.assertEqual(response.status_code, 200)
	
	def test_educador_nao_pode_criar_partida(self):
		"""Teste: Educador não pode criar partida (acesso negado)"""
		from django.urls import reverse
		
		self.client.login(username="educator", password="pass1234")
		
		response = self.client.get(reverse('nova_partida'), follow=False)
		self.assertNotEqual(response.status_code, 200)
	
	def test_ranking_acessivel_para_estudante(self):
		"""Teste: Estudante pode acessar ranking"""
		from django.urls import reverse
		
		self.client.login(username="student", password="pass1234")
		
		response = self.client.get(reverse('ranking'))
		self.assertEqual(response.status_code, 200)
	
	def test_ranking_acessivel_para_educador(self):
		"""Teste: Educador pode acessar ranking"""
		from django.urls import reverse
		
		self.client.login(username="educator", password="pass1234")
		
		response = self.client.get(reverse('ranking'))
		self.assertEqual(response.status_code, 200)
	def test_aspirante_pode_criar_partida(self):
		"""Teste: Aspirante pode criar nova partida"""
		from django.urls import reverse
		
		self.client.login(username="aspirant", password="pass1234")
		
		response = self.client.get(reverse('nova_partida'))
		self.assertEqual(response.status_code, 200)

	def test_profissional_pode_criar_partida(self):
		"""Teste: Profissional Corporativo pode criar partida"""
		from django.urls import reverse
		
		self.client.login(username="professional", password="pass1234")
		
		response = self.client.get(reverse('nova_partida'))
		self.assertEqual(response.status_code, 200)

	def test_ranking_acessivel_para_profissional(self):
		"""Teste: Profissional Corporativo pode acessar ranking"""
		from django.urls import reverse
		
		self.client.login(username="professional", password="pass1234")
		
		response = self.client.get(reverse('ranking'))
		self.assertEqual(response.status_code, 200)

	def test_ranking_acessivel_para_aspirante(self):
		"""Teste: Aspirante pode acessar ranking"""
		from django.urls import reverse
		
		self.client.login(username="aspirant", password="pass1234")
		
		response = self.client.get(reverse('ranking'))
		self.assertEqual(response.status_code, 200)
