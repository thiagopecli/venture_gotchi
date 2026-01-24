# Testes do Venture Gotchi

Este diretório contém todos os testes organizados por categoria.

## Estrutura dos Testes

### 1. test_authentication.py
**Testes iniciais do fluxo de autenticação**
- Registro de usuário
- Login e logout
- Proteção de views autenticadas
- Validação de credenciais

### 2. test_models.py
**Testes unitários da Modelagem**
- Testes do modelo User
- Testes do modelo Startup
- Testes do modelo Turma
- Validações e constraints

### 3. test_rankings.py
**Testes dos rankings e relatórios**
- Sistema de ranking geral
- Ranking de turmas
- Métricas e relatórios de educadores
- Análise de desempenho

### 4. test_integration.py
**Testes de integração (views + models)**
- Fluxo completo do jogo
- Integração perfil e edição
- Integração com turmas
- Comunicação entre componentes

### 5. test_usability.py
**Teste completo de usabilidade e navegação**
- Navegação entre páginas
- Acessibilidade básica
- Usabilidade da interface
- Fluxos completos de trabalho

### 6. test_security.py
**Revisão da arquitetura e segurança**
- Controle de acesso
- Permissões por tipo de usuário
- Proteção contra SQL injection e XSS
- Validação de dados
- Isolamento de dados entre usuários

### 7. test_final.py
**Testes finais + depuração**
- Testes de regressão
- Performance e otimização
- Casos extremos e limites
- Tratamento de erros
- Integridade do banco de dados

## Como Executar os Testes

### Executar todos os testes:
```bash
python manage.py test tests
```

### Executar uma categoria específica:
```bash
python manage.py test tests.test_authentication
python manage.py test tests.test_models
python manage.py test tests.test_rankings
python manage.py test tests.test_integration
python manage.py test tests.test_usability
python manage.py test tests.test_security
python manage.py test tests.test_final
```

### Executar um teste específico:
```bash
python manage.py test tests.test_authentication.AuthenticationFlowTests.test_user_registration
```

### Executar com verbosidade:
```bash
python manage.py test tests --verbosity=2
```

### Executar com cobertura (requer coverage):
```bash
pip install coverage
coverage run --source='.' manage.py test tests
coverage report
coverage html
```

## Convenções

- Cada arquivo de teste corresponde a uma categoria específica
- Os testes seguem o padrão `test_<funcionalidade>`
- Classes de teste herdam de `django.test.TestCase`
- Método `setUp()` é usado para configuração inicial
- Use `subTest` para testes paramétricos

## Dependências para Testes

```bash
pip install coverage  # Para análise de cobertura
pip install django-debug-toolbar  # Para debug
```

## Ordem Sugerida de Execução

1. `test_models.py` - Validar base de dados
2. `test_authentication.py` - Validar acesso
3. `test_security.py` - Validar segurança
4. `test_integration.py` - Validar integração
5. `test_rankings.py` - Validar funcionalidades específicas
6. `test_usability.py` - Validar experiência do usuário
7. `test_final.py` - Testes de regressão e validação final

## Notas Importantes

- Todos os testes usam banco de dados de teste (isolado)
- Os dados são limpos após cada teste
- Configure variáveis de ambiente antes de executar testes sensíveis
- Ajuste os testes conforme a implementação real das suas views e models
