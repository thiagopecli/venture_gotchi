from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView

class PaginaLogin(LoginView):
    template_name = 'login.html'

from .models import Partida, Startup, HistoricoDecisao 

@login_required 
def dashboard(request):
    """
    Lista as partidas existentes do usuário, ordenadas da mais recente.
    """
    partidas = Partida.objects.filter(usuario=request.user).order_by('-data_inicio')
    context = {'partidas': partidas}
    
    return render(request, 'dashboard.html', context) 

@login_required
def nova_partida(request):
    """
    Processa o formulário de criação de nova partida e inicializa a startup.
    """
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        
        Startup.objects.create(partida=partida, saldo_caixa=10000.00)
        
        return redirect('carregar_jogo', partida_id=partida.id)  # type: ignore
    
    return render(request, 'nova_partida.html')

@login_required
def salvar_jogo(request, partida_id):
    """
    Lógica crítica: Recebe os dados do jogo (POST) e persiste no BDR.
    """
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
        
        try:
            startup = partida.startup  # type: ignore # Acessa a métrica via relação OneToOne
            try:
                saldo_novo = float(request.POST.get('saldo_atual', startup.saldo_caixa))
                startup.saldo_caixa = saldo_novo
            except (ValueError, TypeError):
                pass
            
            startup.turno_atual = startup.turno_atual + 1 
            startup.save()
            
            turno_atual = startup.turno_atual
        except Startup.DoesNotExist:
             turno_atual = 1

        decisao_tomada = request.POST.get('decisao', 'Decisão não especificada.')
        
        HistoricoDecisao.objects.create(
            partida=partida,
            decisao_tomada=decisao_tomada,
            turno=turno_atual
        )
    
    return redirect('dashboard')

@login_required
def carregar_jogo(request, partida_id):
    """
    Busca os dados no BDR e prepara o contexto para restaurar o estado do jogo.
    """
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)

    startup_estado = partida.startup  # type: ignore # Último estado das métricas
    historico_decisoes = partida.decisoes.all().order_by('turno')  # type: ignore # Log de decisões

    context = {
        'partida': partida,
        'estado_startup': startup_estado,
        'historico_decisoes': historico_decisoes,
    }
    
    return render(request, 'jogo.html', context)