from core.models import Conquista, ConquistaDesbloqueada, Partida
from decimal import Decimal

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

def verificar_conquistas_progesso(usuario):
    
    conquista, _ = Conquista.objects.get_or_create(
        titulo='Persistente!',
        defaults={
            'descricao': 'Você jogou 5 turnos.',
            'tipo': 'progresso',
            'valor_objetivo': Decimal('5'),
            'pontos': 10,
            'ativo': True,
        }
    )

    partidas = Partida.objects.filter(usuario=usuario)
    for partida in partidas:
        turno_atual = 0
        if hasattr(partida, 'startup') and partida.startup is not None:
            turno_atual = getattr(partida.startup, 'turno_atual', 0)
        if turno_atual >= 5:
            ConquistaDesbloqueada.objects.get_or_create(
                partida=partida,
                conquista=conquista,
                defaults={'turno': turno_atual}
            )