#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Turma, Partida

# Buscar todas as turmas
turmas = Turma.objects.all()

print(f"Total de turmas no banco: {turmas.count()}\n")

turmas_vazias = []

for turma in turmas:
    # Contar alunos dessa turma
    alunos_count = User.objects.filter(
        categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO, 
        codigo_turma__iexact=turma.codigo
    ).count()
    
    # Contar partidas dessa turma
    partidas_count = Partida.objects.filter(
        usuario__codigo_turma__iexact=turma.codigo
    ).count()
    
    print(f"Turma: {turma.codigo} - {turma.nome}")
    print(f"  Alunos: {alunos_count}")
    print(f"  Partidas: {partidas_count}")
    
    if alunos_count == 0 and partidas_count == 0:
        turmas_vazias.append(turma)
        print(f"  ✗ VAZIA - Será deletada")
    else:
        print(f"  ✓ Com dados")
    print()

# Deletar turmas vazias
if turmas_vazias:
    print(f"\n=== DELETANDO {len(turmas_vazias)} TURMAS VAZIAS ===")
    for turma in turmas_vazias:
        print(f"Deletando: {turma.codigo} - {turma.nome}")
        turma.delete()
    print(f"\n✓ {len(turmas_vazias)} turmas deletadas com sucesso!")
else:
    print("\n✓ Nenhuma turma vazia encontrada!")

print(f"\nTotal de turmas restantes: {Turma.objects.count()}")
