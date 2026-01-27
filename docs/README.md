# Venture Gotchi - Da ideia ao Sucesso: Aprendendo Empreendedorismo na Prática

## 📋 Índice
1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [O Desafio Técnico](#o-desafio-técnico)
3. [Solução Proposta](#solução-proposta)
4. [Stack Tecnológica](#stack-tecnológica)
5. [Modelagem de Dados](#modelagem-de-dados)
6. [Público-Alvo](#público-alvo)
7. [Como Executar o Projeto](#como-executar-o-projeto)
8. [Estrutura do Projeto](#estrutura-do-projeto)
9. [Testes](#testes)
10. [Segurança](#segurança)

---

## Visão Geral do Projeto

**Nome do Projeto:** Venture Gotchi - Da ideia ao Sucesso: Aprendendo Empreendedorismo na Prática.

**Resumo Executivo:** O Venture Gotchi é uma plataforma gamificada focada no ensino de empreendedorismo. O objetivo é simular o ciclo de vida de uma startup, permitindo que os alunos aprendam na prática tomando decisões de negócios em um ambiente seguro e interativo.

---

## O Desafio Técnico

### Situação Atual
O projeto já conta com uma interface (Frontend) e uma lógica de aplicação, porém não possui um banco de dados estruturado. Atualmente, isso impede a persistência dos dados, ou seja, o registro de progresso das partidas é perdido ou não armazenado de forma eficiente, impossibilitando a criação de históricos e relatórios.

### Objetivo da Sprint/Fase
Projetar e implementar um Banco de Dados Relacional (SQL) robusto. A meta é sair de um modelo sem persistência para uma arquitetura capaz de suportar múltiplos jogadores, garantindo a integridade dos dados e permitindo análises futuras.

---

## Solução Proposta

A implementação do banco de dados habilitará as seguintes funcionalidades críticas:

- **Continuidade:** O usuário pode parar e retomar a partida de onde parou.
- **Competitividade:** Criação de rankings globais e regionais baseados em métricas persistidas.
- **Análise Educacional:** Geração de relatórios detalhados sobre o desempenho dos alunos para educadores.
- **Escalabilidade:** Preparação do sistema para integração futura com Sistemas de Gestão de Aprendizagem (LMS).

---

## Stack Tecnológica

As tecnologias definidas para o ecossistema do projeto são:

- **Backend:** Python com Django
  - Justificativa: Utilização do framework Django para agilidade no desenvolvimento, aproveitando sua arquitetura MVT (Model-View-Template) e o poderoso ORM para gerenciamento de dados. Uso de JSON para comunicação e troca de dados entre front e back.

- **Banco de Dados:** PostgreSQL
  - Justificativa: Banco de dados relacional robusto para garantir a integridade das transações do jogo (ACID), essencial para salvar o progresso das partidas e histórico financeiro das startups virtuais.

- **Frontend:** React (Estrutura) com CSS (Estilização)

- **Outras Tecnologias:** Git (Versionamento), Virtualenv (Isolamento de ambiente)

---

## Modelagem de Dados

O banco de dados contém as seguintes entidades principais:

- **Usuários:** Dados cadastrais e de login
- **Partidas:** Controle de sessão e estado atual do jogo
- **Fundador:** Atributos do avatar/personagem do jogador
- **Startups:** A entidade virtual gerenciada pelo jogador
- **Métricas da Startup:** Histórico financeiro, moral da equipe, market share
- **Histórico de Decisões:** Registro das escolhas feitas (log de auditoria do jogo)
- **Conquistas/Eventos:** Gamification e marcos atingidos
- **Turmas:** Agrupamento de usuários (educadores podem gerenciar turmas)

**Requisito Técnico:** Garantir a criação correta de chaves estrangeiras (Foreign Keys), constraints (restrições de integridade) e índices para otimização de performance.

---

## Público-Alvo

O sistema é desenhado para atender quatro perfis principais:

1. **Estudantes Universitários (18–25 anos):** Buscam aprendizado prático e engajador.
2. **Aspirantes a Empreendedores (25–35 anos):** Querem simular cenários antes de abrir negócios reais.
3. **Profissionais Corporativos (30–45 anos):** Interessados em intraempreendedorismo e gestão.
4. **Educadores de Negócios (30–50 anos):** Utilizam a ferramenta como apoio didático e avaliação.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes)
- Virtualenv (recomendado)

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/thiagopecli/venture_gotchi.git
   cd venture_gotchi
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env` (copie do `.env.example`):**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

5. **Execute as migrações do banco de dados:**
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário (admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicie o servidor de desenvolvimento:**
   ```bash
   python manage.py runserver
   ```

8. **Acesse a aplicação:**
   - Aplicação: http://localhost:8000
   - Painel Admin: http://localhost:8000/admin

---

## 📁 Estrutura do Projeto

```
venture_gotchi/
├── config/              # Configurações do Django
│   ├── settings.py     # Configurações principais
│   ├── urls.py         # Roteamento de URLs
│   ├── wsgi.py         # Configuração WSGI
│   └── asgi.py         # Configuração ASGI
├── core/                # Aplicação principal
│   ├── models.py       # Modelos de dados
│   ├── views.py        # Views/Lógica
│   ├── urls.py         # Rotas da aplicação
│   ├── forms.py        # Formulários Django
│   ├── admin.py        # Configuração admin
│   ├── permissions.py  # Classes de permissão
│   └── services/       # Serviços de negócio
├── templates/           # Templates HTML
├── static/              # Arquivos estáticos (CSS, JS)
├── tests/               # Suite completa de testes
├── manage.py            # Script de gerenciamento
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

---

## 🧪 Testes

### Status Atual dos Testes

✅ **374 testes passando**  
✅ **Cobertura Geral: 99%** (1097 statements)  
✅ **core/forms.py: 98%** (270 statements)  
✅ **core/views.py: 99%** (356 statements)

### Estrutura dos Testes

#### Testes Fundamentais

1. **test_authentication.py** - Testes do fluxo de autenticação
   - Registro de usuário
   - Login e logout
   - Proteção de views autenticadas
   - Validação de credenciais

2. **test_models.py** - Testes unitários dos modelos
   - Testes do modelo User
   - Testes do modelo Startup
   - Testes do modelo Turma
   - Validações e constraints

3. **test_rankings.py** - Testes dos rankings e relatórios
   - Sistema de ranking geral
   - Ranking de turmas
   - Métricas e relatórios de educadores
   - Análise de desempenho

4. **test_integration.py** - Testes de integração (views + models)
   - Fluxo completo do jogo
   - Integração perfil e edição
   - Integração com turmas
   - Comunicação entre componentes

5. **test_usability.py** - Teste completo de usabilidade e navegação
   - Navegação entre páginas
   - Acessibilidade básica
   - Usabilidade da interface
   - Fluxos completos de trabalho

6. **test_security.py** - Revisão da arquitetura e segurança
   - Controle de acesso
   - Permissões por tipo de usuário
   - Proteção contra SQL injection e XSS
   - Validação de dados
   - Isolamento de dados entre usuários

7. **test_final.py** - Testes finais + depuração
   - Testes de regressão
   - Performance e otimização
   - Casos extremos e limites
   - Tratamento de erros
   - Integridade do banco de dados

#### Testes de Cobertura (Novos)

8. **test_coverage_missing.py** - Cobertura de branches faltantes
   - Testes de decoradores unauthenticated
   - Testes de permissões específicas
   - Testes do filtro `moeda_br` em custom_filters

9. **test_coverage_gaps.py** - Cobertura de cenários específicos
   - Testes de categorias de usuário
   - Fluxos alternativos e edge cases
   - Validações de campo

10. **test_forms_views_full.py** - Cobertura completa de forms e views (Fase 1)
    - 47 testes cobrindo branches de formulários
    - Testes de validação de CadastroUsuarioForm
    - Testes de validação de EditarPerfilForm
    - Testes de views principais

11. **test_forms_views_100pct.py** - Cobertura complementar para 99% (Fase 2)
    - 46 testes adicionais para atingir 99%
    - Testes de branches de clean methods customizados
    - Testes de save() com localização pré-existente
    - Testes de redirect_handler, editar_perfil, educador_editar_perfil
    - Testes de rankings com múltiplos filtros

### Como Executar os Testes

**Executar todos os testes:**
```bash
python manage.py test tests
```

**Executar uma categoria específica:**
```bash
python manage.py test tests.test_authentication
python manage.py test tests.test_models
python manage.py test tests.test_rankings
python manage.py test tests.test_integration
python manage.py test tests.test_usability
python manage.py test tests.test_security
python manage.py test tests.test_final
```

**Executar testes de cobertura:**
```bash
python manage.py test tests.test_coverage_missing
python manage.py test tests.test_coverage_gaps
python manage.py test tests.test_forms_views_full
python manage.py test tests.test_forms_views_100pct
```

**Executar um teste específico:**
```bash
python manage.py test tests.test_authentication.AuthenticationFlowTests.test_user_registration
```

**Executar com verbosidade:**
```bash
python manage.py test tests --verbosity=2
```

### Análise de Cobertura

**Instalar coverage:**
```bash
pip install coverage
```

**Rodar todos os testes com coverage:**
```bash
coverage run --source='core' manage.py test tests
```

**Gerar relatório no terminal:**
```bash
coverage report
```

**Gerar relatório detalhado (HTML):**
```bash
coverage html
# Abrir htmlcov/index.html no navegador
```

**Relatório específico para forms.py e views.py:**
```bash
coverage report --show-missing core/forms.py core/views.py
```

### Arquivos Modificados para Cobertura

- **core/models.py:** Removido método `is_empresa()` (código morto - categoria EMPRESA nunca foi implementada)
- **core/views.py:** Adicionada captura de `InvalidOperation` em `formatar_moeda_br()` para melhor tratamento de erros
- **core/templatetags/custom_filters.py:** Adicionada captura de `InvalidOperation` em `moeda_br()` para melhor tratamento de erros

### Convenções de Testes

- Cada arquivo de teste corresponde a uma categoria específica
- Os testes seguem o padrão `test_<funcionalidade>`
- Classes de teste herdam de `django.test.TestCase`
- Método `setUp()` é usado para configuração inicial
- Use `subTest` para testes paramétricos
- Testes de cobertura usam mock e validação de branches específicos

### Ordem Sugerida de Execução

1. `test_models.py` - Validar base de dados
2. `test_authentication.py` - Validar acesso
3. `test_security.py` - Validar segurança
4. `test_integration.py` - Validar integração
5. `test_rankings.py` - Validar funcionalidades específicas
6. `test_usability.py` - Validar experiência do usuário
7. `test_final.py` - Testes de regressão e validação final

---

## 🗄️ Modelos de Dados

### Partida
- ID da partida
- Usuário (FK)
- Nome da empresa
- Data de início

### Startup
- ID da startup
- Partida (OneToOne)
- Saldo em caixa
- Turno atual
- Nome
- Receita mensal
- Valuation
- Funcionários

### HistoricoDecisao
- ID
- Partida (FK)
- Decisão tomada
- Turno
- Data da decisão

---

## ✅ Melhorias Implementadas

✅ Removido import duplicado em models.py  
✅ Mudança de FloatField para DecimalField (valores monetários)  
✅ Adicionadas meta classes em modelos  
✅ Validação melhorada em views.py  
✅ Arquivo `.env.example` para variáveis de ambiente  
✅ Arquivo `.gitignore` para versionamento  
✅ Documentação completa no README  
✅ Suite completa de 374 testes com 99% cobertura  
✅ Tratamento robusto de exceções (InvalidOperation)

---

## 🔒 Segurança

- [ ] Mover SECRET_KEY para arquivo .env
- [ ] Separar configurações de desenvolvimento e produção
- [ ] Adicionar validação de formulários com Django Forms
- [ ] Implementar CSRF token em todos os formulários
- [ ] Usar environment variables para dados sensíveis
- [x] Controle de acesso baseado em papel (Role-Based Access Control)
- [x] Proteção de views autenticadas
- [x] Isolamento de dados entre usuários

---

## 📚 Dependências para Testes

```bash
pip install coverage  # Para análise de cobertura
pip install django-debug-toolbar  # Para debug
```

---

## 📝 Licença

Este projeto é de código aberto. Veja LICENSE para detalhes.

---

## 👨‍💻 Desenvolvedor

Thiago Pereira - [GitHub](https://github.com/thiagopecli)

---

## 🔄 Fluxo de Desenvolvimento

### Criando uma nova branch:
```bash
git checkout -b feature/sua-feature
```

### Sempre partir da main:
```bash
git checkout main
git pull origin main
git checkout -b feature/sua-feature
```

### Ativando o ambiente virtual e instalando dependências:
```bash
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Verificando alterações no BD:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📌 Notas Importantes

- Todos os testes usam banco de dados de teste (isolado)
- Os dados são limpos após cada teste
- Configure variáveis de ambiente antes de executar testes sensíveis
- Ajuste os testes conforme a implementação real das suas views e models
- Mantenha a cobertura acima de 95%
- Execute todos os testes antes de fazer push de uma feature

---

Link para Acessar o Sistema: https://venture-gotchi.onrender.com/login/

**Última atualização:** 25 de janeiro de 2026
