# Venture Gotchi - Simulador de Startups

## 📋 O Que É?

**Venture Gotchi** é uma aplicação web educacional que simula a experiência de empreender e gerenciar uma startup. É um simulador de negócios interativo que combina elementos de gamificação com aprendizado prático sobre gestão empresarial.

A plataforma foi desenvolvida em **Django** (Python) e oferece uma experiência completa para diferentes tipos de usuários, desde estudantes universitários até educadores e profissionais corporativos.

---

## 🎮 Funcionalidades Principais

### Para Jogadores (Estudantes, Aspirantes e Profissionais)

- **Criar e Gerenciar Partidas**: Inicie uma nova simulação de startup com seu próprio nome de empresa
- **Tomar Decisões Estratégicas**: Faça escolhas importantes que afetam métricas como:
  - Saldo em caixa (capital disponível)
  - Receita mensal
  - Valuation (valor da empresa)
  - Número de funcionários
  
- **Progresso por Turnos**: A simulação funciona em turnos, onde cada turno representa um período de tempo (dia, semana ou mês)

- **Histórico de Decisões**: Acompanhe todas as decisões tomadas ao longo da partida

- **Ranking Global**: Veja como você se compara com outros jogadores baseado em métricas como valuation, receita e funcionários

- **Conquistas e Badges**: Desbloqueie conquistas especiais ao atingir certas metas durante a partida

- **Salvar e Carregar**: Interrompa sua partida e continue depois do ponto onde parou

### Para Educadores

- **Criar Turmas**: Organize grupos de estudantes para acompanhar
- **Relatórios Agregados**: Veja métricas consolidadas do desempenho de sua turma
- **Análise de Turma**: Acompanhe o progresso individual e coletivo dos alunos
- **Dashboard Educador**: Interface específica para gerenciar turmas e visualizar dados

---

## 👥 Tipos de Usuários

1. **Estudante Universitário** (`ESTUDANTE_UNIVERSITARIO`)
   - Pode jogar e usar todas as funcionalidades de simulação
   - Pode ver ranking e conquistas
   - Pode fazer parte de turmas de educadores

2. **Aspirante a Empreendedor** (`ASPIRANTE_EMPREENDEDOR`)
   - Acesso completo ao jogo e simulador
   - Mesmas permissões que estudante

3. **Educador de Negócios** (`EDUCADOR_NEGOCIOS`)
   - Pode criar e gerenciar turmas
   - Acesso a relatórios agregados de seus alunos
   - Visualiza métricas consolidadas

4. **Profissional Corporativo** (`PROFISSIONAL_CORPORATIVO`)
   - Acesso ao jogo e simulador
   - Pode participar de rankings e ver conquistas

---

## 🏗️ Arquitetura Técnica

### Stack Tecnológico

- **Backend**: Django 6.0 (Python)
- **Banco de Dados**: 
  - SQLite (desenvolvimento local)
  - PostgreSQL (produção no Render)
- **Frontend**: Templates Django + HTML/CSS
- **Servidor**: Gunicorn + WhiteNoise (servir arquivos estáticos)
- **Autenticação**: Django Auth com User customizado

### Modelos Principais de Dados

- **User**: Usuário customizado que estende AbstractUser com categorias e perfil
- **Turma**: Grupos de estudantes criados por educadores
- **Partida**: Uma sessão de jogo individual
- **Startup**: Métricas e estado da empresa durante a partida
- **HistoricoDecisao**: Registro de todas as decisões tomadas
- **Fundador**: Perfil do empreendedor (nome, idade, experiência)
- **Evento**: Eventos que podem impactar a startup durante a simulação
- **ConquistaDesbloqueada**: Badges e conquistas desbloqueadas pelo jogador

### Estrutura de Diretórios

```
venture_gotchi/
├── config/              # Configurações Django
│   ├── settings.py     # Variáveis de ambiente, apps, middleware
│   ├── urls.py         # Roteamento principal
│   ├── wsgi.py         # Configuração WSGI
│   └── asgi.py         # Configuração ASGI
│
├── core/               # Aplicação principal
│   ├── models.py       # Modelos de dados (User, Partida, etc)
│   ├── views.py        # Lógica das views (controllers)
│   ├── forms.py        # Formulários Django
│   ├── urls.py         # Roteamento da app
│   ├── permissions.py  # Decoradores de permissão
│   ├── admin.py        # Interface administrativa
│   └── services/       # Serviços de negócio
│       └── conquistas.py  # Lógica de desbloqueio de conquistas
│
├── templates/          # Templates HTML
├── static/            # Arquivos CSS, JS, imagens
├── tests/             # Suite de testes
├── docs/              # Documentação
└── manage.py          # Utilitário Django
```

---

## 🔐 Sistema de Permissões

A aplicação usa decoradores customizados para controlar acesso:

- `@estudante_required`: Apenas estudantes
- `@educador_required`: Apenas educadores
- `@pode_salvar_partida`: Usuários que podem salvar/carregar partidas
- `@pode_acessar_relatorios`: Educadores acessarem relatórios
- `@pode_acessar_ranking`: Usuários que podem ver rankings

---

## 📊 Principais Métricas Rastreadas

Cada partida rastreia:

- **Saldo em Caixa**: Capital disponível
- **Receita Mensal**: Faturamento regular
- **Valuation**: Valor total da empresa
- **Funcionários**: Número de pessoas na equipe
- **Turno Atual**: Período de tempo decorrido na simulação

---

## 🎯 Objetivo da Aplicação

Venture Gotchi é um **simulador educacional** que:

1. Ensina princípios de gestão de startups
2. Permite experiência prática em tomada de decisões empresariais
3. Proporciona feedback imediato sobre consequências de escolhas
4. Engaja estudantes através de gamificação (rankings, conquistas)
5. Oferece ferramentas aos educadores para acompanhar alunos

É especialmente útil para:
- Cursos de empreendedorismo
- Disciplinas de gestão empresarial
- Desenvolvimento de habilidades de liderança
- Aprendizado prático sobre métricas de startup

---

## 🚀 Recursos Futuros Potenciais

- Competições entre turmas
- Novos tipos de eventos e desafios
- Integração com APIs de dados reais
- Modo multiplayer (competição em tempo real)
- Análises preditivas com IA
- Mobile app
- Certificações ao completar módulos

---

## 📝 Licença e Autor

Projeto desenvolvido para **Panthe On Ltda**

---

## 📚 Documentação Adicional

Consulte os outros arquivos na pasta `docs/`:
- `GUIA_INICIANTE.md` - Como rodar pela primeira vez
- `VALIDACOES_FORMULARIO.md` - Validações de entrada
- `CONFORMIDADE.md` - Requisitos de conformidade
