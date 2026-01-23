#!/usr/bin/env python
import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Turma, Startup, Partida, Conquista

# Criar um educador (se não existir)
educador, _ = User.objects.get_or_create(
    username='educador_teste',
    defaults={
        'email': 'educador@teste.com',
        'first_name': 'João',
        'last_name': 'Silva',
        'categoria': 'EDUCADOR_NEGOCIOS'
    }
)

# Criar 3 turmas
turma1_codigo = Turma.gerar_codigo_unico()
turma1 = Turma.objects.create(
    codigo=turma1_codigo,
    nome='Empreendedorismo 2026.1',
    descricao='Turma de primeiro semestre com foco em startups de tecnologia e inovação.',
    educador=educador,
    ativa=True
)

turma2_codigo = Turma.gerar_codigo_unico()
turma2 = Turma.objects.create(
    codigo=turma2_codigo,
    nome='Gestão de Negócios 2026.1',
    descricao='Turma especializada em gestão empresarial e modelo de negócio.',
    educador=educador,
    ativa=True
)

turma3_codigo = Turma.gerar_codigo_unico()
turma3 = Turma.objects.create(
    codigo=turma3_codigo,
    nome='Inovação e Sustentabilidade 2026.1',
    descricao='Turma voltada para startups com impacto social e ambiental.',
    educador=educador,
    ativa=True
)

print(f"✓ Turma 1 criada: {turma1.codigo} - {turma1.nome}")
print(f"✓ Turma 2 criada: {turma2.codigo} - {turma2.nome}")
print(f"✓ Turma 3 criada: {turma3.codigo} - {turma3.nome}")

# Criar alunos e startups para Turma 1
turma1_startups = []
alunos_turma1 = []
for i in range(4):
    aluno, _ = User.objects.get_or_create(
        username=f'aluno_turma1_{i+1}',
        defaults={
            'email': f'aluno{i+1}@turma1.com',
            'first_name': f'Aluno {i+1}',
            'categoria': 'ESTUDANTE_UNIVERSITARIO',
            'codigo_turma': turma1.codigo
        }
    )
    if _ and not aluno.has_usable_password():
        aluno.set_password('senha123')
        aluno.save()
    alunos_turma1.append(aluno)
    
    # Criar partida primeiro
    partida, _ = Partida.objects.get_or_create(
        usuario=aluno,
        nome_empresa=f'TechStart {i+1}',
        defaults={'ativa': True}
    )
    
    # Criar startup baseado na partida
    startup, _ = Startup.objects.get_or_create(
        partida=partida,
        defaults={
            'nome': f'TechStart {i+1}',
            'saldo_caixa': Decimal(random.randint(50000, 500000)),
            'valuation': Decimal(random.randint(100000, 2000000)),
            'receita_mensal': Decimal(random.randint(10000, 100000)),
            'turno_atual': 1,
            'funcionarios': random.randint(1, 20)
        }
    )
    turma1_startups.append(startup)

print(f"✓ {len(alunos_turma1)} alunos e startups criados para Turma 1")

# Criar alunos e startups para Turma 2
turma2_startups = []
alunos_turma2 = []
for i in range(3):
    aluno, _ = User.objects.get_or_create(
        username=f'aluno_turma2_{i+1}',
        defaults={
            'email': f'aluno{i+1}@turma2.com',
            'first_name': f'Gerenciador {i+1}',
            'categoria': 'ESTUDANTE_UNIVERSITARIO',
            'codigo_turma': turma2.codigo
        }
    )
    if _ and not aluno.has_usable_password():
        aluno.set_password('senha123')
        aluno.save()
    alunos_turma2.append(aluno)
    
    # Criar partida primeiro
    partida, _ = Partida.objects.get_or_create(
        usuario=aluno,
        nome_empresa=f'BusinessFlow {i+1}',
        defaults={'ativa': True}
    )
    
    # Criar startup baseado na partida
    startup, _ = Startup.objects.get_or_create(
        partida=partida,
        defaults={
            'nome': f'BusinessFlow {i+1}',
            'saldo_caixa': Decimal(random.randint(80000, 600000)),
            'valuation': Decimal(random.randint(500000, 3000000)),
            'receita_mensal': Decimal(random.randint(30000, 150000)),
            'turno_atual': 1,
            'funcionarios': random.randint(5, 30)
        }
    )
    turma2_startups.append(startup)

print(f"✓ {len(alunos_turma2)} alunos e startups criados para Turma 2")

# Criar alunos e startups para Turma 3
turma3_startups = []
alunos_turma3 = []
for i in range(5):
    aluno, _ = User.objects.get_or_create(
        username=f'aluno_turma3_{i+1}',
        defaults={
            'email': f'aluno{i+1}@turma3.com',
            'first_name': f'Empreendedor {i+1}',
            'categoria': 'ESTUDANTE_UNIVERSITARIO',
            'codigo_turma': turma3.codigo
        }
    )
    if _ and not aluno.has_usable_password():
        aluno.set_password('senha123')
        aluno.save()
    alunos_turma3.append(aluno)
    
    # Criar partida primeiro
    partida, _ = Partida.objects.get_or_create(
        usuario=aluno,
        nome_empresa=f'EcoStart {i+1}',
        defaults={'ativa': True}
    )
    
    # Criar startup baseado na partida
    startup, _ = Startup.objects.get_or_create(
        partida=partida,
        defaults={
            'nome': f'EcoStart {i+1}',
            'saldo_caixa': Decimal(random.randint(40000, 450000)),
            'valuation': Decimal(random.randint(150000, 1500000)),
            'receita_mensal': Decimal(random.randint(15000, 80000)),
            'turno_atual': 1,
            'funcionarios': random.randint(2, 15)
        }
    )
    turma3_startups.append(startup)

print(f"✓ {len(alunos_turma3)} alunos e startups criados para Turma 3")

print("✓ Conquistas fictícias adicionadas")
print("\n=== RESUMO ===")
print(f"Total de turmas: {Turma.objects.count()}")
print(f"Total de alunos: {User.objects.filter(categoria='ESTUDANTE_UNIVERSITARIO').count()}")
print(f"Total de startups: {Startup.objects.count()}")
print(f"Total de partidas: {Partida.objects.count()}")
