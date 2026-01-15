# Sistema de Permissões - Venture Gotchi

## Visão Geral

O sistema de permissões foi implementado para controlar o acesso às funcionalidades baseado no tipo de usuário cadastrado.

## Tipos de Usuário

### 1. Estudante/Aspirante
**Categorias:**
- `ALUNO` - Aluno (CPF)
- `STARTUP_PF` - Startup (CPF - Pré-formalizada)
- `STARTUP_PJ` - Startup (CNPJ)

**Permissões:**
- ✅ Salvar e Carregar Partida
- ✅ Visualizar Dados de Partida (Própria)
- ✅ Gerenciar Conquistas (Desbloquear)
- ❌ Acessar/Gerar Relatórios Agregados
- ✅ Acessar Ranking

### 2. Educador de Negócios
**Categorias:**
- `PROFESSOR` - Professor (CPF)
- `INSTITUICAO` - Instituição de Ensino (CNPJ)

**Permissões:**
- ❌ Salvar e Carregar Partida (Somente leitura dos dados)
- ❌ Visualizar Dados de Partida (Própria)
- ❌ Gerenciar Conquistas (Apenas visualizar)
- ✅ Acessar/Gerar Relatórios Agregados
- ✅ Acessar Ranking (compartilhado com Estudantes)

### 3. Empresa
**Categoria:**
- `EMPRESA` - Empresa (CNPJ)

**Permissões:**
- Definir conforme necessidade futura

## Métodos de Verificação (Model User)

```python
# Verificação de tipo de usuário
user.is_estudante()  # True se for Aluno, Startup PF/PJ
user.is_educador()   # True se for Professor, Instituição
user.is_empresa()    # True se for Empresa

# Verificação de permissões específicas
user.pode_salvar_carregar_partida()         # Estudantes
user.pode_visualizar_propria_partida()      # Estudantes
user.pode_acessar_relatorios_agregados()    # Educadores
user.pode_acessar_ranking()                 # Educadores
user.pode_desbloquear_conquistas()          # Estudantes
user.pode_visualizar_conquistas()           # Todos
```

## Decorators Disponíveis

### @estudante_required
Permite acesso apenas para Estudantes/Aspirantes.

```python
@estudante_required
def minha_view(request):
    # Somente estudantes podem acessar
    pass
```

### @educador_required
Permite acesso apenas para Educadores de Negócios.

```python
@educador_required
def relatorios(request):
    # Somente educadores podem acessar
    pass
```

### @pode_salvar_partida
Verifica se o usuário pode salvar/carregar partidas.

```python
@pode_salvar_partida
def nova_partida(request):
    # Verifica permissão para criar partidas
    pass
```

### @pode_acessar_relatorios
Verifica se o usuário pode acessar relatórios agregados.

```python
@pode_acessar_relatorios
def relatorios_view(request):
    # Somente usuários com permissão podem acessar
    pass
```

### @pode_acessar_ranking
Verifica se o usuário pode acessar ranking.

```python
@pode_acessar_ranking
def ranking_view(request):
    # Somente usuários com permissão podem acessar
    pass
```

## Views Protegidas

### Aplicadas automaticamente:
- `nova_partida` - Requer `@pode_salvar_partida`
- `salvar_jogo` - Requer `@pode_salvar_partida`
- Outras views mantêm `@login_required` apenas

## Templates - Verificação de Permissões

Nos templates, você pode usar:

```django
{% if user.is_estudante %}
    <!-- Conteúdo para estudantes -->
{% endif %}

{% if user.is_educador %}
    <!-- Conteúdo para educadores -->
{% endif %}

{% if user.pode_salvar_carregar_partida %}
    <a href="{% url 'nova_partida' %}">Nova Partida</a>
{% endif %}
```

## Dashboard Adaptativo

O dashboard agora se adapta ao tipo de usuário:

### Estudante
- Exibe partidas salvas
- Botão para criar nova startup
- Acesso ao jogo completo

### Educador
- Exibe funcionalidades de educador
- Links para relatórios e rankings (em desenvolvimento)
- Não pode criar partidas

## Mensagens de Erro

Quando um usuário tenta acessar uma funcionalidade sem permissão:

- Redirecionado para o dashboard
- Mensagem de erro clara explicando a restrição
- Indicação do tipo de usuário necessário

## Próximos Passos

1. Implementar views de relatórios agregados para educadores
2. Criar sistema de ranking
3. Adicionar permissões específicas para tipo `EMPRESA`
4. Implementar logs de acesso por tipo de usuário
