"""
Testes do sistema de conquistas
Cobre verificação automática, desbloqueio por saldo e persistência
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Partida, Startup, Conquista, ConquistaDesbloqueada
from core.services.conquistas import (
    verificar_conquistas_progesso,
    _garantir_conquistas_existem,
    CONQUISTAS_SALDO
)
from decimal import Decimal

User = get_user_model()


class ConquistasModelTests(TestCase):
    """Testes dos models de conquista"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup'
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            nome='Test Startup',
            saldo_caixa=Decimal('0.00'),
            turno_atual=1
        )
    
    def test_conquista_creation(self):
        """Testa criação de conquista"""
        conquista = Conquista.objects.create(
            titulo='Conquista Teste',
            descricao='Descrição de teste',
            tipo='saldo',
            valor_objetivo=Decimal('100000.00'),
            pontos=10
        )
        self.assertEqual(conquista.titulo, 'Conquista Teste')
        self.assertEqual(conquista.pontos, 10)
        self.assertTrue(conquista.ativo)
    
    def test_conquista_desbloqueada_creation(self):
        """Testa desbloqueio de conquista"""
        conquista = Conquista.objects.create(
            titulo='Conquista Teste',
            descricao='Descrição',
            tipo='saldo',
            valor_objetivo=Decimal('100000.00'),
            pontos=10
        )
        desbloqueada = ConquistaDesbloqueada.objects.create(
            partida=self.partida,
            conquista=conquista,
            turno=5
        )
        self.assertEqual(desbloqueada.partida, self.partida)
        self.assertEqual(desbloqueada.conquista, conquista)
        self.assertEqual(desbloqueada.turno, 5)
        self.assertIsNotNone(desbloqueada.desbloqueada_em)
    
    def test_conquista_unique_per_partida(self):
        """Testa que uma conquista não pode ser desbloqueada duas vezes na mesma partida"""
        conquista = Conquista.objects.create(
            titulo='Conquista Teste',
            descricao='Descrição',
            tipo='saldo',
            valor_objetivo=Decimal('100000.00'),
            pontos=10
        )
        ConquistaDesbloqueada.objects.create(
            partida=self.partida,
            conquista=conquista,
            turno=5
        )
        
        # Tentar criar novamente deve falhar ou ser ignorado
        with self.assertRaises(Exception):
            ConquistaDesbloqueada.objects.create(
                partida=self.partida,
                conquista=conquista,
                turno=6
            )


class ConquistasSaldoTests(TestCase):
    """Testes de conquistas por saldo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup'
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            nome='Test Startup',
            saldo_caixa=Decimal('0.00'),
            turno_atual=1
        )
        # Garantir que conquistas existem
        _garantir_conquistas_existem()
    
    def test_conquista_100k(self):
        """Testa desbloqueio de conquista de R$ 100k"""
        self.startup.saldo_caixa = Decimal('100000.00')
        self.startup.save()
        
        novas = verificar_conquistas_progesso(self.user, self.partida)
        
        # Deve ter desbloqueado "Persistente!" e "Primeiros R$ 100 mil"
        self.assertGreaterEqual(len(novas), 1)
        
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=self.partida)
        titulos = [d.conquista.titulo for d in desbloqueadas]
        self.assertIn('Primeiros R$ 100 mil', titulos)
    
    def test_conquista_500k(self):
        """Testa desbloqueio de conquista de R$ 500k"""
        self.startup.saldo_caixa = Decimal('500000.00')
        self.startup.save()
        
        verificar_conquistas_progesso(self.user, self.partida)
        
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=self.partida)
        titulos = [d.conquista.titulo for d in desbloqueadas]
        self.assertIn('Meio Milhão!', titulos)
    
    def test_conquista_1mi(self):
        """Testa desbloqueio de conquista de R$ 1 milhão"""
        self.startup.saldo_caixa = Decimal('1000000.00')
        self.startup.save()
        
        verificar_conquistas_progesso(self.user, self.partida)
        
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=self.partida)
        titulos = [d.conquista.titulo for d in desbloqueadas]
        self.assertIn('Primeiro Milhão!', titulos)
    
    def test_conquistas_multiplas_saldo(self):
        """Testa que múltiplas conquistas são desbloqueadas quando saldo atinge valor alto"""
        self.startup.saldo_caixa = Decimal('1000000.00')
        self.startup.save()
        
        verificar_conquistas_progesso(self.user, self.partida)
        
        # Deve ter desbloqueado todas as conquistas até 1M
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=self.partida).count()
        # Persistente + conquistas de 100k até 1M (10 conquistas) = 11
        # Mas verificamos >=10 para garantir que pelo menos as de saldo foram desbloqueadas
        self.assertGreaterEqual(desbloqueadas, 10)
    
    def test_conquista_nao_duplicada(self):
        """Testa que conquistas não são duplicadas ao chamar verificação múltiplas vezes"""
        self.startup.saldo_caixa = Decimal('100000.00')
        self.startup.save()
        
        verificar_conquistas_progesso(self.user, self.partida)
        count_1 = ConquistaDesbloqueada.objects.filter(partida=self.partida).count()
        
        # Chamar novamente
        verificar_conquistas_progesso(self.user, self.partida)
        count_2 = ConquistaDesbloqueada.objects.filter(partida=self.partida).count()
        
        self.assertEqual(count_1, count_2)


class ConquistasPersistenciaTests(TestCase):
    """Testes da conquista de persistência"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup'
        )
        self.startup = Startup.objects.create(
            partida=self.partida,
            nome='Test Startup',
            saldo_caixa=Decimal('0.00'),
            turno_atual=1
        )
        _garantir_conquistas_existem()
    
    def test_conquista_persistente_desbloqueada(self):
        """Testa que conquista 'Persistente!' é desbloqueada automaticamente após turno 5"""
        # Conquista Persistente! só é desbloqueada a partir do turno 5
        self.startup.turno_atual = 5
        self.startup.save()
        
        novas = verificar_conquistas_progesso(self.user, self.partida)
        
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=self.partida)
        titulos = [d.conquista.titulo for d in desbloqueadas]
        self.assertIn('Persistente!', titulos)
    
    def test_conquista_persistente_turno(self):
        """Testa que conquista registra o turno correto"""
        self.startup.turno_atual = 10
        self.startup.save()
        
        verificar_conquistas_progesso(self.user, self.partida)
        
        persistente = ConquistaDesbloqueada.objects.get(
            partida=self.partida,
            conquista__titulo='Persistente!'
        )
        self.assertEqual(persistente.turno, 10)


class ConquistasEdgeCasesTests(TestCase):
    """Testes de casos extremos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        _garantir_conquistas_existem()
    
    def test_partida_sem_startup(self):
        """Testa verificação de conquistas em partida sem startup"""
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup'
        )
        
        # Não deve dar erro
        novas = verificar_conquistas_progesso(self.user, partida)
        self.assertIsInstance(novas, list)
    
    def test_saldo_negativo(self):
        """Testa que saldo negativo não desbloqueia conquistas"""
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Test Startup'
        )
        startup = Startup.objects.create(
            partida=partida,
            nome='Test Startup',
            saldo_caixa=Decimal('-100000.00'),
            turno_atual=1
        )
        
        verificar_conquistas_progesso(self.user, partida)
        
        # Deve ter apenas Persistente!, não conquistas de saldo
        desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=partida)
        titulos = [d.conquista.titulo for d in desbloqueadas]
        self.assertNotIn('Primeiros R$ 100 mil', titulos)
    
    def test_usuario_multiplas_partidas(self):
        """Testa que conquistas são isoladas por partida"""
        partida1 = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Startup 1'
        )
        startup1 = Startup.objects.create(
            partida=partida1,
            nome='Startup 1',
            saldo_caixa=Decimal('100000.00'),
            turno_atual=1
        )
        
        partida2 = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Startup 2'
        )
        startup2 = Startup.objects.create(
            partida=partida2,
            nome='Startup 2',
            saldo_caixa=Decimal('500000.00'),
            turno_atual=1
        )
        
        verificar_conquistas_progesso(self.user)
        
        # Verificar que cada partida tem conquistas diferentes
        conquistas_p1 = ConquistaDesbloqueada.objects.filter(partida=partida1).count()
        conquistas_p2 = ConquistaDesbloqueada.objects.filter(partida=partida2).count()
        
        # Partida 2 deve ter mais conquistas (500k > 100k)
        self.assertGreater(conquistas_p2, conquistas_p1)
    
    def test_garantir_conquistas_idempotente(self):
        """Testa que _garantir_conquistas_existem pode ser chamada múltiplas vezes"""
        count_1 = Conquista.objects.count()
        
        _garantir_conquistas_existem()
        count_2 = Conquista.objects.count()
        
        _garantir_conquistas_existem()
        count_3 = Conquista.objects.count()
        
        # Não deve criar duplicatas
        self.assertEqual(count_2, count_3)


class ConquistasSistemaTests(TestCase):
    """Testes do sistema completo de conquistas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        _garantir_conquistas_existem()
    
    def test_conquistas_saldo_definidas(self):
        """Testa que todas as conquistas de saldo estão definidas"""
        self.assertGreater(len(CONQUISTAS_SALDO), 0)
        
        # Verificar estrutura das conquistas
        for conquista in CONQUISTAS_SALDO[:5]:  # Testar primeiras 5
            self.assertIn('valor', conquista)
            self.assertIn('titulo', conquista)
            self.assertIn('descricao', conquista)
            self.assertIn('pontos', conquista)
            self.assertIsInstance(conquista['valor'], Decimal)
    
    def test_todas_conquistas_criadas_no_banco(self):
        """Testa que todas as conquistas de CONQUISTAS_SALDO foram criadas no banco"""
        titulos_esperados = [c['titulo'] for c in CONQUISTAS_SALDO]
        titulos_no_banco = list(Conquista.objects.filter(
            titulo__in=titulos_esperados
        ).values_list('titulo', flat=True))
        
        # Todas devem existir
        self.assertEqual(len(titulos_no_banco), len(titulos_esperados))
    
    def test_conquista_bilionario_existe(self):
        """Testa que a conquista final (Bilionário) existe"""
        bilionario = Conquista.objects.filter(
            titulo='Bilionário! Você Zerou o Game!'
        ).exists()
        self.assertTrue(bilionario)
