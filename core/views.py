from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView

class LoginView(LoginView):
    template_name = 'login.html'

# Modelos agora DESCOMENTADOS e prontos para uso:
from .models import Partida, Startup, HistoricoDecisao 
# Note: Eles precisam existir no core/models.py para o código funcionar.

# 1. TELA INICIAL / DASHBOARD DO USUÁRIO
@login_required 
def dashboard(request):
    """
    Lista as partidas existentes do usuário, ordenadas da mais recente.
    """
    # Filtra as partidas pertencentes ao usuário logado (Parte da Ana)
    partidas = Partida.objects.filter(usuario=request.user).order_by('-data_inicio')
    
    context = {'partidas': partidas}
    
    # Template path ajustado para 'dashboard.html'
    return render(request, 'dashboard.html', context) 

# 2. NOVA PARTIDA (Requisito 4.2 - Cadastro de Partidas)
@login_required
def nova_partida(request):
    """
    Processa o formulário de criação de nova partida e inicializa a startup.
    """
    if request.method == 'POST':
        # Assumindo que o formulário envia o campo 'nome_empresa'
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        
        # 1. Cria a Partida
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        
        # 2. Inicializa a Startup com valores padrão (e.g., 10000.00 de caixa)
        # Isso é essencial para o salvamento e relatórios
        Startup.objects.create(partida=partida, saldo_caixa=10000.00)
        
        # 3. Redireciona para o jogo, carregando a partida recém-criada
        return redirect('carregar_jogo', partida_id=partida.id)
    
    # Template path ajustado para 'nova_partida.html'
    return render(request, 'nova_partida.html')

# 3. SALVAR PROGRESSO (Requisito 4.2 - Salvamento)
@login_required
def salvar_jogo(request, partida_id):
    """
    Lógica crítica: Recebe os dados do jogo (POST) e persiste no BDR.
    """
    if request.method == 'POST':
        # 1. Busca a partida (seguro: verifica se pertence ao usuário)
        partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
        
        # 2. Atualiza as métricas da Startup (Assume que o frontend envia os dados atualizados)
        try:
            startup = partida.startup # Acessa a métrica via relação OneToOne
            startup.saldo_caixa = float(request.POST.get('saldo_atual', startup.saldo_caixa))
            startup.turno_atual = startup.turno_atual + 1 
            startup.save()
            
            turno_atual = startup.turno_atual
        except Startup.DoesNotExist:
             turno_atual = 1 # Se a métrica não existir, usa o turno 1 como fallback

        # 3. Registra o histórico de decisão
        decisao_tomada = request.POST.get('decisao', 'Decisão não especificada.')
        
        HistoricoDecisao.objects.create(
            partida=partida,
            decisao_tomada=decisao_tomada,
            turno=turno_atual
        )
    
    # Redireciona o usuário de volta para o Dashboard após salvar
    return redirect('dashboard')

# 4. CARREGAR JOGO (Requisito 4.2 - Continuidade)
@login_required
def carregar_jogo(request, partida_id):
    """
    Busca os dados no BDR e prepara o contexto para restaurar o estado do jogo.
    """
    # Busca a partida (seguro: verifica se pertence ao usuário)
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)

    # Recupera todos os dados necessários para rodar o jogo
    startup_estado = partida.startup # Último estado das métricas
    historico_decisoes = partida.decisoes.all().order_by('turno') # Log de decisões

    context = {
        'partida': partida,
        'estado_startup': startup_estado,
        'historico_decisoes': historico_decisoes,
    }
    
    # Template para exibir a tela de jogo
    return render(request, 'jogo.html', context)