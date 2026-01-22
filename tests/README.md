# Testes do Venture Gotchi

Esta pasta contém todos os testes automatizados do projeto.

## Estrutura

- `test_core.py` - Testes principais da aplicação core
  - `ORMOptimizationTests` - Testes de otimização de queries ORM
  - `NavigationFlowTests` - Testes de fluxo de navegação e usabilidade
  - `GameStateTests` - Testes de estados e transições do jogo
  - `PermissionTests` - Testes de permissões e controle de acesso

## Como Executar

### Executar todos os testes:
```bash
python manage.py test tests
```

### Executar testes de uma classe específica:
```bash
python manage.py test tests.test_core.PermissionTests
```

### Executar um teste específico:
```bash
python manage.py test tests.test_core.PermissionTests.test_profissional_pode_criar_partida
```

### Executar com verbosidade:
```bash
python manage.py test tests -v 2
```

## Cobertura de Testes

- ✅ Testes de ORM e otimização de queries
- ✅ Testes de fluxo completo de navegação
- ✅ Testes de autenticação e permissões
- ✅ Testes de estados do jogo (game over, vitória)
- ✅ Testes de decisões e impactos nas métricas
- ✅ Testes de histórico e conquistas
- ✅ Testes de ranking

## Total: 47 testes automatizados
