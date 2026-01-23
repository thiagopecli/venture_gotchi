from core.models import Conquista, ConquistaDesbloqueada, Partida
from decimal import Decimal

# Definição das conquistas de saldo
CONQUISTAS_SALDO = [
    # Conquistas a cada 100 mil até 1 milhão
    {'valor': Decimal('100000.00'), 'titulo': 'Primeiros R$ 100 mil', 'descricao': 'Você alcançou R$ 100.000 no caixa!', 'pontos': 10},
    {'valor': Decimal('200000.00'), 'titulo': 'R$ 200 mil no Caixa', 'descricao': 'Você alcançou R$ 200.000 no caixa!', 'pontos': 15},
    {'valor': Decimal('300000.00'), 'titulo': 'R$ 300 mil no Caixa', 'descricao': 'Você alcançou R$ 300.000 no caixa!', 'pontos': 20},
    {'valor': Decimal('400000.00'), 'titulo': 'R$ 400 mil no Caixa', 'descricao': 'Você alcançou R$ 400.000 no caixa!', 'pontos': 25},
    {'valor': Decimal('500000.00'), 'titulo': 'Meio Milhão!', 'descricao': 'Você alcançou R$ 500.000 no caixa!', 'pontos': 30},
    {'valor': Decimal('600000.00'), 'titulo': 'R$ 600 mil no Caixa', 'descricao': 'Você alcançou R$ 600.000 no caixa!', 'pontos': 35},
    {'valor': Decimal('700000.00'), 'titulo': 'R$ 700 mil no Caixa', 'descricao': 'Você alcançou R$ 700.000 no caixa!', 'pontos': 40},
    {'valor': Decimal('800000.00'), 'titulo': 'R$ 800 mil no Caixa', 'descricao': 'Você alcançou R$ 800.000 no caixa!', 'pontos': 45},
    {'valor': Decimal('900000.00'), 'titulo': 'R$ 900 mil no Caixa', 'descricao': 'Você alcançou R$ 900.000 no caixa!', 'pontos': 50},
    {'valor': Decimal('1000000.00'), 'titulo': 'Primeiro Milhão!', 'descricao': 'Você alcançou seu primeiro milhão no caixa!', 'pontos': 100},
    
    # Conquistas a cada 10 milhões até 1 bilhão
    {'valor': Decimal('10000000.00'), 'titulo': 'R$ 10 Milhões!', 'descricao': 'Você alcançou R$ 10 milhões no caixa!', 'pontos': 150},
    {'valor': Decimal('20000000.00'), 'titulo': 'R$ 20 Milhões!', 'descricao': 'Você alcançou R$ 20 milhões no caixa!', 'pontos': 200},
    {'valor': Decimal('30000000.00'), 'titulo': 'R$ 30 Milhões!', 'descricao': 'Você alcançou R$ 30 milhões no caixa!', 'pontos': 250},
    {'valor': Decimal('40000000.00'), 'titulo': 'R$ 40 Milhões!', 'descricao': 'Você alcançou R$ 40 milhões no caixa!', 'pontos': 300},
    {'valor': Decimal('50000000.00'), 'titulo': 'R$ 50 Milhões!', 'descricao': 'Você alcançou R$ 50 milhões no caixa!', 'pontos': 350},
    {'valor': Decimal('60000000.00'), 'titulo': 'R$ 60 Milhões!', 'descricao': 'Você alcançou R$ 60 milhões no caixa!', 'pontos': 400},
    {'valor': Decimal('70000000.00'), 'titulo': 'R$ 70 Milhões!', 'descricao': 'Você alcançou R$ 70 milhões no caixa!', 'pontos': 450},
    {'valor': Decimal('80000000.00'), 'titulo': 'R$ 80 Milhões!', 'descricao': 'Você alcançou R$ 80 milhões no caixa!', 'pontos': 500},
    {'valor': Decimal('90000000.00'), 'titulo': 'R$ 90 Milhões!', 'descricao': 'Você alcançou R$ 90 milhões no caixa!', 'pontos': 550},
    {'valor': Decimal('100000000.00'), 'titulo': 'R$ 100 Milhões!', 'descricao': 'Você alcançou R$ 100 milhões no caixa!', 'pontos': 600},
    {'valor': Decimal('110000000.00'), 'titulo': 'R$ 110 Milhões!', 'descricao': 'Você alcançou R$ 110 milhões no caixa!', 'pontos': 650},
    {'valor': Decimal('120000000.00'), 'titulo': 'R$ 120 Milhões!', 'descricao': 'Você alcançou R$ 120 milhões no caixa!', 'pontos': 700},
    {'valor': Decimal('130000000.00'), 'titulo': 'R$ 130 Milhões!', 'descricao': 'Você alcançou R$ 130 milhões no caixa!', 'pontos': 750},
    {'valor': Decimal('140000000.00'), 'titulo': 'R$ 140 Milhões!', 'descricao': 'Você alcançou R$ 140 milhões no caixa!', 'pontos': 800},
    {'valor': Decimal('150000000.00'), 'titulo': 'R$ 150 Milhões!', 'descricao': 'Você alcançou R$ 150 milhões no caixa!', 'pontos': 850},
    {'valor': Decimal('160000000.00'), 'titulo': 'R$ 160 Milhões!', 'descricao': 'Você alcançou R$ 160 milhões no caixa!', 'pontos': 900},
    {'valor': Decimal('170000000.00'), 'titulo': 'R$ 170 Milhões!', 'descricao': 'Você alcançou R$ 170 milhões no caixa!', 'pontos': 950},
    {'valor': Decimal('180000000.00'), 'titulo': 'R$ 180 Milhões!', 'descricao': 'Você alcançou R$ 180 milhões no caixa!', 'pontos': 1000},
    {'valor': Decimal('190000000.00'), 'titulo': 'R$ 190 Milhões!', 'descricao': 'Você alcançou R$ 190 milhões no caixa!', 'pontos': 1050},
    {'valor': Decimal('200000000.00'), 'titulo': 'R$ 200 Milhões!', 'descricao': 'Você alcançou R$ 200 milhões no caixa!', 'pontos': 1100},
    {'valor': Decimal('210000000.00'), 'titulo': 'R$ 210 Milhões!', 'descricao': 'Você alcançou R$ 210 milhões no caixa!', 'pontos': 1150},
    {'valor': Decimal('220000000.00'), 'titulo': 'R$ 220 Milhões!', 'descricao': 'Você alcançou R$ 220 milhões no caixa!', 'pontos': 1200},
    {'valor': Decimal('230000000.00'), 'titulo': 'R$ 230 Milhões!', 'descricao': 'Você alcançou R$ 230 milhões no caixa!', 'pontos': 1250},
    {'valor': Decimal('240000000.00'), 'titulo': 'R$ 240 Milhões!', 'descricao': 'Você alcançou R$ 240 milhões no caixa!', 'pontos': 1300},
    {'valor': Decimal('250000000.00'), 'titulo': 'R$ 250 Milhões!', 'descricao': 'Você alcançou R$ 250 milhões no caixa!', 'pontos': 1350},
    {'valor': Decimal('260000000.00'), 'titulo': 'R$ 260 Milhões!', 'descricao': 'Você alcançou R$ 260 milhões no caixa!', 'pontos': 1400},
    {'valor': Decimal('270000000.00'), 'titulo': 'R$ 270 Milhões!', 'descricao': 'Você alcançou R$ 270 milhões no caixa!', 'pontos': 1450},
    {'valor': Decimal('280000000.00'), 'titulo': 'R$ 280 Milhões!', 'descricao': 'Você alcançou R$ 280 milhões no caixa!', 'pontos': 1500},
    {'valor': Decimal('290000000.00'), 'titulo': 'R$ 290 Milhões!', 'descricao': 'Você alcançou R$ 290 milhões no caixa!', 'pontos': 1550},
    {'valor': Decimal('300000000.00'), 'titulo': 'R$ 300 Milhões!', 'descricao': 'Você alcançou R$ 300 milhões no caixa!', 'pontos': 1600},
    {'valor': Decimal('310000000.00'), 'titulo': 'R$ 310 Milhões!', 'descricao': 'Você alcançou R$ 310 milhões no caixa!', 'pontos': 1650},
    {'valor': Decimal('320000000.00'), 'titulo': 'R$ 320 Milhões!', 'descricao': 'Você alcançou R$ 320 milhões no caixa!', 'pontos': 1700},
    {'valor': Decimal('330000000.00'), 'titulo': 'R$ 330 Milhões!', 'descricao': 'Você alcançou R$ 330 milhões no caixa!', 'pontos': 1750},
    {'valor': Decimal('340000000.00'), 'titulo': 'R$ 340 Milhões!', 'descricao': 'Você alcançou R$ 340 milhões no caixa!', 'pontos': 1800},
    {'valor': Decimal('350000000.00'), 'titulo': 'R$ 350 Milhões!', 'descricao': 'Você alcançou R$ 350 milhões no caixa!', 'pontos': 1850},
    {'valor': Decimal('360000000.00'), 'titulo': 'R$ 360 Milhões!', 'descricao': 'Você alcançou R$ 360 milhões no caixa!', 'pontos': 1900},
    {'valor': Decimal('370000000.00'), 'titulo': 'R$ 370 Milhões!', 'descricao': 'Você alcançou R$ 370 milhões no caixa!', 'pontos': 1950},
    {'valor': Decimal('380000000.00'), 'titulo': 'R$ 380 Milhões!', 'descricao': 'Você alcançou R$ 380 milhões no caixa!', 'pontos': 2000},
    {'valor': Decimal('390000000.00'), 'titulo': 'R$ 390 Milhões!', 'descricao': 'Você alcançou R$ 390 milhões no caixa!', 'pontos': 2050},
    {'valor': Decimal('400000000.00'), 'titulo': 'R$ 400 Milhões!', 'descricao': 'Você alcançou R$ 400 milhões no caixa!', 'pontos': 2100},
    {'valor': Decimal('410000000.00'), 'titulo': 'R$ 410 Milhões!', 'descricao': 'Você alcançou R$ 410 milhões no caixa!', 'pontos': 2150},
    {'valor': Decimal('420000000.00'), 'titulo': 'R$ 420 Milhões!', 'descricao': 'Você alcançou R$ 420 milhões no caixa!', 'pontos': 2200},
    {'valor': Decimal('430000000.00'), 'titulo': 'R$ 430 Milhões!', 'descricao': 'Você alcançou R$ 430 milhões no caixa!', 'pontos': 2250},
    {'valor': Decimal('440000000.00'), 'titulo': 'R$ 440 Milhões!', 'descricao': 'Você alcançou R$ 440 milhões no caixa!', 'pontos': 2300},
    {'valor': Decimal('450000000.00'), 'titulo': 'R$ 450 Milhões!', 'descricao': 'Você alcançou R$ 450 milhões no caixa!', 'pontos': 2350},
    {'valor': Decimal('460000000.00'), 'titulo': 'R$ 460 Milhões!', 'descricao': 'Você alcançou R$ 460 milhões no caixa!', 'pontos': 2400},
    {'valor': Decimal('470000000.00'), 'titulo': 'R$ 470 Milhões!', 'descricao': 'Você alcançou R$ 470 milhões no caixa!', 'pontos': 2450},
    {'valor': Decimal('480000000.00'), 'titulo': 'R$ 480 Milhões!', 'descricao': 'Você alcançou R$ 480 milhões no caixa!', 'pontos': 2500},
    {'valor': Decimal('490000000.00'), 'titulo': 'R$ 490 Milhões!', 'descricao': 'Você alcançou R$ 490 milhões no caixa!', 'pontos': 2550},
    {'valor': Decimal('500000000.00'), 'titulo': 'Meio Bilhão!', 'descricao': 'Você alcançou meio bilhão no caixa!', 'pontos': 2600},
    {'valor': Decimal('510000000.00'), 'titulo': 'R$ 510 Milhões!', 'descricao': 'Você alcançou R$ 510 milhões no caixa!', 'pontos': 2650},
    {'valor': Decimal('520000000.00'), 'titulo': 'R$ 520 Milhões!', 'descricao': 'Você alcançou R$ 520 milhões no caixa!', 'pontos': 2700},
    {'valor': Decimal('530000000.00'), 'titulo': 'R$ 530 Milhões!', 'descricao': 'Você alcançou R$ 530 milhões no caixa!', 'pontos': 2750},
    {'valor': Decimal('540000000.00'), 'titulo': 'R$ 540 Milhões!', 'descricao': 'Você alcançou R$ 540 milhões no caixa!', 'pontos': 2800},
    {'valor': Decimal('550000000.00'), 'titulo': 'R$ 550 Milhões!', 'descricao': 'Você alcançou R$ 550 milhões no caixa!', 'pontos': 2850},
    {'valor': Decimal('560000000.00'), 'titulo': 'R$ 560 Milhões!', 'descricao': 'Você alcançou R$ 560 milhões no caixa!', 'pontos': 2900},
    {'valor': Decimal('570000000.00'), 'titulo': 'R$ 570 Milhões!', 'descricao': 'Você alcançou R$ 570 milhões no caixa!', 'pontos': 2950},
    {'valor': Decimal('580000000.00'), 'titulo': 'R$ 580 Milhões!', 'descricao': 'Você alcançou R$ 580 milhões no caixa!', 'pontos': 3000},
    {'valor': Decimal('590000000.00'), 'titulo': 'R$ 590 Milhões!', 'descricao': 'Você alcançou R$ 590 milhões no caixa!', 'pontos': 3050},
    {'valor': Decimal('600000000.00'), 'titulo': 'R$ 600 Milhões!', 'descricao': 'Você alcançou R$ 600 milhões no caixa!', 'pontos': 3100},
    {'valor': Decimal('610000000.00'), 'titulo': 'R$ 610 Milhões!', 'descricao': 'Você alcançou R$ 610 milhões no caixa!', 'pontos': 3150},
    {'valor': Decimal('620000000.00'), 'titulo': 'R$ 620 Milhões!', 'descricao': 'Você alcançou R$ 620 milhões no caixa!', 'pontos': 3200},
    {'valor': Decimal('630000000.00'), 'titulo': 'R$ 630 Milhões!', 'descricao': 'Você alcançou R$ 630 milhões no caixa!', 'pontos': 3250},
    {'valor': Decimal('640000000.00'), 'titulo': 'R$ 640 Milhões!', 'descricao': 'Você alcançou R$ 640 milhões no caixa!', 'pontos': 3300},
    {'valor': Decimal('650000000.00'), 'titulo': 'R$ 650 Milhões!', 'descricao': 'Você alcançou R$ 650 milhões no caixa!', 'pontos': 3350},
    {'valor': Decimal('660000000.00'), 'titulo': 'R$ 660 Milhões!', 'descricao': 'Você alcançou R$ 660 milhões no caixa!', 'pontos': 3400},
    {'valor': Decimal('670000000.00'), 'titulo': 'R$ 670 Milhões!', 'descricao': 'Você alcançou R$ 670 milhões no caixa!', 'pontos': 3450},
    {'valor': Decimal('680000000.00'), 'titulo': 'R$ 680 Milhões!', 'descricao': 'Você alcançou R$ 680 milhões no caixa!', 'pontos': 3500},
    {'valor': Decimal('690000000.00'), 'titulo': 'R$ 690 Milhões!', 'descricao': 'Você alcançou R$ 690 milhões no caixa!', 'pontos': 3550},
    {'valor': Decimal('700000000.00'), 'titulo': 'R$ 700 Milhões!', 'descricao': 'Você alcançou R$ 700 milhões no caixa!', 'pontos': 3600},
    {'valor': Decimal('710000000.00'), 'titulo': 'R$ 710 Milhões!', 'descricao': 'Você alcançou R$ 710 milhões no caixa!', 'pontos': 3650},
    {'valor': Decimal('720000000.00'), 'titulo': 'R$ 720 Milhões!', 'descricao': 'Você alcançou R$ 720 milhões no caixa!', 'pontos': 3700},
    {'valor': Decimal('730000000.00'), 'titulo': 'R$ 730 Milhões!', 'descricao': 'Você alcançou R$ 730 milhões no caixa!', 'pontos': 3750},
    {'valor': Decimal('740000000.00'), 'titulo': 'R$ 740 Milhões!', 'descricao': 'Você alcançou R$ 740 milhões no caixa!', 'pontos': 3800},
    {'valor': Decimal('750000000.00'), 'titulo': 'R$ 750 Milhões!', 'descricao': 'Você alcançou R$ 750 milhões no caixa!', 'pontos': 3850},
    {'valor': Decimal('760000000.00'), 'titulo': 'R$ 760 Milhões!', 'descricao': 'Você alcançou R$ 760 milhões no caixa!', 'pontos': 3900},
    {'valor': Decimal('770000000.00'), 'titulo': 'R$ 770 Milhões!', 'descricao': 'Você alcançou R$ 770 milhões no caixa!', 'pontos': 3950},
    {'valor': Decimal('780000000.00'), 'titulo': 'R$ 780 Milhões!', 'descricao': 'Você alcançou R$ 780 milhões no caixa!', 'pontos': 4000},
    {'valor': Decimal('790000000.00'), 'titulo': 'R$ 790 Milhões!', 'descricao': 'Você alcançou R$ 790 milhões no caixa!', 'pontos': 4050},
    {'valor': Decimal('800000000.00'), 'titulo': 'R$ 800 Milhões!', 'descricao': 'Você alcançou R$ 800 milhões no caixa!', 'pontos': 4100},
    {'valor': Decimal('810000000.00'), 'titulo': 'R$ 810 Milhões!', 'descricao': 'Você alcançou R$ 810 milhões no caixa!', 'pontos': 4150},
    {'valor': Decimal('820000000.00'), 'titulo': 'R$ 820 Milhões!', 'descricao': 'Você alcançou R$ 820 milhões no caixa!', 'pontos': 4200},
    {'valor': Decimal('830000000.00'), 'titulo': 'R$ 830 Milhões!', 'descricao': 'Você alcançou R$ 830 milhões no caixa!', 'pontos': 4250},
    {'valor': Decimal('840000000.00'), 'titulo': 'R$ 840 Milhões!', 'descricao': 'Você alcançou R$ 840 milhões no caixa!', 'pontos': 4300},
    {'valor': Decimal('850000000.00'), 'titulo': 'R$ 850 Milhões!', 'descricao': 'Você alcançou R$ 850 milhões no caixa!', 'pontos': 4350},
    {'valor': Decimal('860000000.00'), 'titulo': 'R$ 860 Milhões!', 'descricao': 'Você alcançou R$ 860 milhões no caixa!', 'pontos': 4400},
    {'valor': Decimal('870000000.00'), 'titulo': 'R$ 870 Milhões!', 'descricao': 'Você alcançou R$ 870 milhões no caixa!', 'pontos': 4450},
    {'valor': Decimal('880000000.00'), 'titulo': 'R$ 880 Milhões!', 'descricao': 'Você alcançou R$ 880 milhões no caixa!', 'pontos': 4500},
    {'valor': Decimal('890000000.00'), 'titulo': 'R$ 890 Milhões!', 'descricao': 'Você alcançou R$ 890 milhões no caixa!', 'pontos': 4550},
    {'valor': Decimal('900000000.00'), 'titulo': 'R$ 900 Milhões!', 'descricao': 'Você alcançou R$ 900 milhões no caixa!', 'pontos': 4600},
    {'valor': Decimal('910000000.00'), 'titulo': 'R$ 910 Milhões!', 'descricao': 'Você alcançou R$ 910 milhões no caixa!', 'pontos': 4650},
    {'valor': Decimal('920000000.00'), 'titulo': 'R$ 920 Milhões!', 'descricao': 'Você alcançou R$ 920 milhões no caixa!', 'pontos': 4700},
    {'valor': Decimal('930000000.00'), 'titulo': 'R$ 930 Milhões!', 'descricao': 'Você alcançou R$ 930 milhões no caixa!', 'pontos': 4750},
    {'valor': Decimal('940000000.00'), 'titulo': 'R$ 940 Milhões!', 'descricao': 'Você alcançou R$ 940 milhões no caixa!', 'pontos': 4800},
    {'valor': Decimal('950000000.00'), 'titulo': 'R$ 950 Milhões!', 'descricao': 'Você alcançou R$ 950 milhões no caixa!', 'pontos': 4850},
    {'valor': Decimal('960000000.00'), 'titulo': 'R$ 960 Milhões!', 'descricao': 'Você alcançou R$ 960 milhões no caixa!', 'pontos': 4900},
    {'valor': Decimal('970000000.00'), 'titulo': 'R$ 970 Milhões!', 'descricao': 'Você alcançou R$ 970 milhões no caixa!', 'pontos': 4950},
    {'valor': Decimal('980000000.00'), 'titulo': 'R$ 980 Milhões!', 'descricao': 'Você alcançou R$ 980 milhões no caixa!', 'pontos': 5000},
    {'valor': Decimal('990000000.00'), 'titulo': 'R$ 990 Milhões!', 'descricao': 'Você alcançou R$ 990 milhões no caixa!', 'pontos': 5050},
    
    # Última conquista - 1 bilhão (zerou o game)
    {'valor': Decimal('1000000000.00'), 'titulo': 'Bilionário! Você Zerou o Game!', 'descricao': 'Parabéns! Você alcançou R$ 1 bilhão e zerou o VentureGotchi!', 'pontos': 10000},
]

def verificar_conquistas_partida(partida):
    conquistas_desbloqueadas = ConquistaDesbloqueada.objects.filter(partida=partida).values_list('conquista_id', flat=True)

    conquista, _ = Conquista.objects.get_or_create(
        titulo='Primeira Simulação',
        defaults={
            'descricao': 'Você completou a primeira simulação!',
            'tipo': 'progresso',
            'valor_objetivo': Decimal('0.00'),
            'pontos': 10,
            'ativo': True,
        }
    )

    if conquista.id not in conquistas_desbloqueadas:
        turno_atual = 1
        if hasattr(partida, 'startup') and partida.startup is not None:
            turno_atual = getattr(partida.startup, 'turno_atual', 1)
        ConquistaDesbloqueada.objects.create(partida=partida, conquista=conquista, turno=turno_atual)

def _garantir_conquistas_existem():
    """
    Garante que todas as conquistas do sistema existem no banco.
    Usa bulk_create para otimização.
    """
    # Verificar se já existem conquistas criadas
    if Conquista.objects.filter(titulo='Bilionário! Você Zerou o Game!').exists():
        return  # Conquistas já criadas
    
    # Criar conquista de persistência
    Conquista.objects.get_or_create(
        titulo='Persistente!',
        defaults={
            'descricao': 'Você jogou 5 turnos.',
            'tipo': 'progresso',
            'valor_objetivo': Decimal('5'),
            'pontos': 10,
            'ativo': True,
        }
    )
    
    # Coletar títulos existentes
    titulos_existentes = set(Conquista.objects.filter(
        titulo__in=[info['titulo'] for info in CONQUISTAS_SALDO]
    ).values_list('titulo', flat=True))
    
    # Criar apenas conquistas que não existem
    conquistas_para_criar = []
    for conquista_info in CONQUISTAS_SALDO:
        if conquista_info['titulo'] not in titulos_existentes:
            conquistas_para_criar.append(Conquista(
                titulo=conquista_info['titulo'],
                descricao=conquista_info['descricao'],
                tipo='progresso',
                valor_objetivo=conquista_info['valor'],
                pontos=conquista_info['pontos'],
                ativo=True,
            ))
    
    # Criar todas de uma vez
    if conquistas_para_criar:
        Conquista.objects.bulk_create(conquistas_para_criar, ignore_conflicts=True)


def verificar_conquistas_progesso(usuario, partida_especifica=None):
    """
    Verifica e desbloqueia conquistas de progresso.
    Retorna lista de novas conquistas desbloqueadas.
    """
    novas_conquistas = []
    
    # Garantir que conquistas existem (otimizado)
    _garantir_conquistas_existem()
    
    # Buscar conquistas necessárias
    conquista_persistente = Conquista.objects.get(titulo='Persistente!')
    conquistas_saldo_map = {
        c.valor_objetivo: c 
        for c in Conquista.objects.filter(
            titulo__in=[info['titulo'] for info in CONQUISTAS_SALDO]
        )
    }

    # Se uma partida específica foi passada, verificar apenas ela
    if partida_especifica:
        partidas = [partida_especifica]
    else:
        partidas = Partida.objects.filter(usuario=usuario).select_related('startup')
    
    for partida in partidas:
        turno_atual = 0
        if hasattr(partida, 'startup') and partida.startup is not None:
            turno_atual = getattr(partida.startup, 'turno_atual', 0)
        if turno_atual >= 5:
            obj, created = ConquistaDesbloqueada.objects.get_or_create(
                partida=partida,
                conquista=conquista_persistente,
                defaults={'turno': turno_atual}
            )
            if created:
                novas_conquistas.append(conquista_persistente)
        
        # Verificar conquistas de saldo
        if hasattr(partida, 'startup') and partida.startup is not None:
            saldo_caixa = getattr(partida.startup, 'saldo_caixa', Decimal('0.00'))
            
            # Desbloquear todas as conquistas alcançadas
            for valor, conquista_obj in conquistas_saldo_map.items():
                if saldo_caixa >= valor:
                    obj, created = ConquistaDesbloqueada.objects.get_or_create(
                        partida=partida,
                        conquista=conquista_obj,
                        defaults={'turno': turno_atual}
                    )
                    if created:
                        novas_conquistas.append(conquista_obj)
    
    return novas_conquistas