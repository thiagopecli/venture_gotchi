# venture_gotchi

1. Visão Geral do Projeto;

    Nome do Projeto: Venture Gotchi - Da ideia ao Sucesso: Aprendendo Empreendedorismo na Prática.
    Resumo Executivo: O Venture Gotchi é uma plataforma gamificada focada no ensino de empreendedorismo. O objetivo é simular o ciclo de vida de uma startup, permitindo que os alunos aprendam na prática tomando decisões de negócios em um ambiente seguro e interativo.

2. O Desafio Técnico (Escopo Atual);

    Situação Atual: O projeto já conta com uma interface (Frontend) e uma lógica de aplicação, porém não possui um banco de dados estruturado. Atualmente, isso impede a persistência dos dados, ou seja, o registro de progresso das partidas é perdido ou não armazenado de forma eficiente, impossibilitando a criação de históricos e relatórios.
    Objetivo da Sprint/Fase: Projetar e implementar um Banco de Dados Relacional (SQL) robusto. A meta é sair de um modelo sem persistência para uma arquitetura capaz de suportar múltiplos jogadores, garantindo a integridade dos dados e permitindo análises futuras.

3. Solução Proposta;

    A implementação do banco de dados habilitará as seguintes funcionalidades críticas:
    Continuidade: O usuário pode parar e retomar a partida de onde parou.
    Competitividade: Criação de rankings globais e regionais baseados em métricas persistidas.
    Análise Educacional: Geração de relatórios detalhados sobre o desempenho dos alunos para educadores.
    Escalabilidade: Preparação do sistema para integração futura com Sistemas de Gestão de Aprendizagem (LMS).

4. Stack Tecnológica (Atualizada);

    As tecnologias definidas para o ecossistema do projeto são:
    Backend: Python com Django.
    Justificativa: Utilização do framework Django para agilidade no desenvolvimento, aproveitando sua arquitetura MVT (Model-View-Template) e o poderoso ORM para gerenciamento de dados. Uso de JSON para comunicação e troca de dados entre front e back.
    Banco de Dados: MySQL.
    Justificativa: Banco de dados relacional robusto para garantir a integridade das transações do jogo (ACID), essencial para salvar o progresso das partidas e histórico financeiro das startups virtuais.
    Frontend: React (Estrutura) com CSS (Estilização).
    Outras Tecnologias: Git (Versionamento), Virtualenv (Isolamento de ambiente).

5. Modelagem de Dados (Core do Desafio);

    O estagiário/desenvolvedor será responsável pela modelagem das seguintes entidades principais:
    Usuários: Dados cadastrais e de login.
    Partidas: Controle de sessão e estado atual do jogo.
    Fundador: Atributos do avatar/personagem do jogador.
    Startups: A entidade virtual gerenciada pelo jogador.
    Métricas da Startup: Histórico financeiro, moral da equipe, market share.
    Histórico de Decisões: Registro das escolhas feitas (log de auditoria do jogo).
    Conquistas/Eventos: Gamification e marcos atingidos.
    Requisito Técnico: Garantir a criação correta de chaves estrangeiras (Foreign Keys), constraints (restrições de integridade) e índices para otimização de performance.

6. Público-Alvo (Personas);

    O sistema é desenhado para atender quatro perfis principais:
    Estudantes Universitários (18–25 anos): Buscam aprendizado prático e engajador.
    Aspirantes a Empreendedores (25–35 anos): Querem simular cenários antes de abrir negócios reais.
    Profissionais Corporativos (30–45 anos): Interessados em intraempreendedorismo e gestão.
    Educadores de Negócios (30–50 anos): Utilizam a ferramenta como apoio didático e avaliação.

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
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
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
│   └── admin.py        # Configuração admin
├── templates/           # Templates HTML
├── static/              # Arquivos estáticos (CSS, JS)
├── manage.py            # Script de gerenciamento
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

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

## ⚙️ Melhorias Implementadas

✅ Removido import duplicado em models.py
✅ Mudança de FloatField para DecimalField (valores monetários)
✅ Adicionadas meta classes em modelos
✅ Validação melhorada em views.py
✅ Arquivo `.env.example` para variáveis de ambiente
✅ Arquivo `.gitignore` para versionamento
✅ Documentação completa no README

---

## 🔒 Segurança

- [ ] Mover SECRET_KEY para arquivo .env
- [ ] Separar configurações de desenvolvimento e produção
- [ ] Adicionar validação de formulários com Django Forms
- [ ] Implementar CSRF token em todos os formulários
- [ ] Usar environment variables para dados sensíveis

---

## 📝 Licença

Este projeto é de código aberto. Veja LICENSE para detalhes.

---

## 👨‍💻 Desenvolvedor

Thiago Pereira - [GitHub](https://github.com/thiagopecli)


Criando branch: git checkout -b thiago_pereira

*** Sempre a partir da main ***

*** Iniciando/ativando a .venv e iniciando servidor ***

Criando o ambiente virtual: py -m venv .venv
Ativando o ambiente virtual: .\.venv\Scripts\activate
Instalando as ferramentas: pip install -r requirements.txt
Entrar na pasta do projeto: cd

# Verificando alterações no BD: 
python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
