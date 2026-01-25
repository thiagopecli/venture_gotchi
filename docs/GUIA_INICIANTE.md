# 🚀 Guia de Primeiros Passos - Venture Gotchi

## Para Pessoas Sem Experiência em Programação

Siga este guia passo a passo para rodar o **Venture Gotchi** no seu computador.

---

## ⚙️ Pré-Requisitos

Você precisa instalar estas 3 coisas **uma única vez**:

### 1️⃣ Python
O Python é a linguagem de programação que o projeto usa.

**Windows:**
1. Acesse [python.org](https://www.python.org/downloads/)
2. Clique no botão grande de download (versão 3.11 ou mais recente)
3. Execute o instalador
4. **IMPORTANTE**: Marque a opção "Add Python to PATH" antes de clicar Install
5. Clique "Install Now"
6. Aguarde a instalação terminar

**Verificar se funcionou:**
- Abra o Command Prompt (pressione `Win + R`, digite `cmd` e pressione Enter)
- Digite: `python --version`
- Deve aparecer algo como: `Python 3.11.x`

### 2️⃣ Git
O Git permite clonar (baixar) o projeto do GitHub.

1. Acesse [git-scm.com](https://git-scm.com/download/win)
2. Clique em "Click here to download"
3. Execute o instalador
4. Clique "Next" em todas as telas (deixar as opções padrão)
5. Clique "Finish"

### 3️⃣ Um Editor de Código
Você pode usar o **Visual Studio Code** (recomendado e gratuito):

1. Acesse [code.visualstudio.com](https://code.visualstudio.com/)
2. Clique em "Download for Windows"
3. Execute o instalador
4. Siga as instruções na tela

---

## 📥 Passo 1: Baixar o Projeto

### Via GitHub (Recomendado)

1. Abra o Command Prompt ou PowerShell
2. Navegue até a pasta onde quer guardar o projeto:
   ```
   cd Desktop
   ```

3. Clone o repositório:
   ```
   git clone https://github.com/thiagopecli/venture_gotchi.git
   ```

4. Entre na pasta do projeto:
   ```
   cd venture_gotchi
   ```

### Ou Manualmente
- Faça download direto do GitHub e extraia em uma pasta no seu Desktop

---

## 🔧 Passo 2: Preparar o Ambiente

Agora você precisa criar um **ambiente virtual** (um espaço isolado para as dependências).

No Command Prompt ou PowerShell, digite:

### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Você deve ver `(.venv)` aparecer no início da linha do terminal.**

---

## 📦 Passo 3: Instalar as Dependências

As dependências são as bibliotecas que o projeto precisa para funcionar.

No terminal (com o ambiente virtual ativo), digite:

```
pip install -r requirements.txt
```

Aguarde até aparecer mensagens dizendo que tudo foi instalado com sucesso.

---

## 🗄️ Passo 4: Preparar o Banco de Dados

O projeto usa um banco de dados SQLite para guardar informações.

Execute estes comandos **em ordem**:

```
python manage.py migrate
```

Este comando cria as tabelas no banco de dados.

---

## 👨‍💻 Passo 5: Criar um Usuário Administrador (Opcional)

Se você quer acessar o painel de administração depois:

```
python manage.py createsuperuser
```

Siga as instruções:
- Username: seu nome de usuário (ex: `admin`)
- Email: seu email
- Password: sua senha (não aparece enquanto digita, é normal)
- Confirm password: repita a senha

---

## 🚀 Passo 6: Rodar o Servidor

Agora sim! Para iniciar o servidor:

```
python manage.py runserver
```

Você deve ver uma mensagem assim:
```
Starting development server at http://127.0.0.1:8000/
```

---

## 🌐 Passo 7: Acessar o Aplicativo

1. Abra seu navegador (Chrome, Firefox, Edge, etc)
2. Digite na barra de endereço: `http://localhost:8000/`
3. Você verá a página de login do Venture Gotchi

---

## 👤 Passo 8: Criar uma Conta

1. Clique em "Registrar-se"
2. Preencha o formulário com seus dados
3. Escolha uma categoria (recomendado: "Aspirante a Empreendedor")
4. Clique em "Registrar"
5. Pronto! Você está logado

---

## 🎮 Passo 9: Começar a Jogar

1. Na dashboard, clique em "Nova Partida"
2. Escolha um nome para sua empresa
3. Configure seu perfil de fundador
4. Clique em "Iniciar"
5. Aproveite! 🎉

---

## ⏹️ Como Parar o Servidor

Para parar o servidor:
- Pressione `Ctrl + C` no terminal
- Aparecerá uma confirmação, pressione `Y` e Enter

---

## 🆘 Troubleshooting (Resolvendo Problemas)

### Erro: "python não é reconhecido"
- **Solução**: Python não foi adicionado ao PATH durante a instalação
- Reinstale Python marcando "Add Python to PATH"

### Erro: "pip não encontrado"
- **Solução**: Use `python -m pip` em vez de `pip`
- Exemplo: `python -m pip install -r requirements.txt`

### Erro: "ModuleNotFoundError"
- **Solução**: Você esqueceu de ativar o ambiente virtual
- Ative novamente conforme o Passo 2

### Porta 8000 já está em uso
- **Solução**: Use uma porta diferente:
  ```
  python manage.py runserver 8001
  ```

### Problemas ao migrar o banco de dados
- **Solução**: Delete o arquivo `db.sqlite3` e rode novamente:
  ```
  python manage.py migrate
  ```

---

## 📝 Estrutura Básica do Projeto

```
venture_gotchi/
├── manage.py           ← Utilitário para rodar comandos Django
├── requirements.txt    ← Lista de dependências
├── config/             ← Configurações do projeto
├── core/               ← Código principal do jogo
├── templates/          ← Páginas HTML
├── static/            ← CSS, imagens
├── tests/             ← Testes automatizados
└── db.sqlite3         ← Banco de dados (criado automaticamente)
```

---

## 🔌 Comandos Úteis Depois de Rodar

```bash
# Ver usuários
python manage.py shell

# Rodar testes
python manage.py test

# Criar nova migração
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Coletar arquivos estáticos (produção)
python manage.py collectstatic
```

---

## 🎯 Próximos Passos

1. Crie várias contas diferentes para testar
2. Experimente diferentes categorias de usuário
3. Consulte `SOBRE_O_PROJETO.md` para entender melhor as funcionalidades
4. Leia `VALIDACOES_FORMULARIO.md` para ver quais campos são obrigatórios

---

## ❓ Dúvidas Frequentes

**P: Preciso estar conectado à internet?**
R: Não! O projeto funciona 100% offline durante o desenvolvimento.

**P: Posso rodar em outro computador?**
R: Sim! Basta repetir os passos 1-6. O banco de dados é local.

**P: Como resetar tudo?**
R: Delete a pasta `.venv` e o arquivo `db.sqlite3`, depois repita a partir do Passo 2.

**P: E se for em macOS ou Linux?**
R: Os passos são praticamente iguais, só muda a forma de ativar o ambiente virtual (Passo 2).

---

## 📞 Suporte

Se tiver dúvidas:
1. Revise os passos acima
2. Consulte a seção "Troubleshooting"
3. Procure a mensagem de erro no Google
4. Abra uma issue no GitHub do projeto

---

## 🎉 Parabéns!

Você conseguiu rodar o Venture Gotchi! Agora é só aproveitar e se divertir aprendendo sobre startups.

Bom jogo! 🚀
