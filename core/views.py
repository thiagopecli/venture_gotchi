from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from .models import Partida, Startup, HistoricoDecisao 

# --- TELA DE ENTRADA ---

def index(request):
    """
    Página inicial pública (Boas-vindas). 
    Removido o redirecionamento automático para evitar o erro ERR_TOO_MANY_REDIRECTS.
    """
    return render(request, 'index.html')

# --- AUTENTICAÇÃO E REGISTRO ---

class PaginaLogin(LoginView):
    template_name = 'login.html'

def registrar(request):
    """
    Cria novos usuários no sistema (Requisito: Usuários).
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registro.html', {'form': form})

# --- GESTÃO DE PARTIDAS (Sua Responsabilidade Principal) ---

@login_required 
def dashboard(request):
    """
    Lista partidas do usuário (Requisito: Continuidade/Histórico).
    """
    partidas = Partida.objects.filter(usuario=request.user).order_by('-data_inicio')
    context = {'partidas': partidas}
    return render(request, 'dashboard.html', context) 

@login_required
def nova_partida(request):
    """
    Cria nova simulação e inicializa a startup (Requisito: Cadastro de Partidas).
    """
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        # Inicializa a startup com saldo padrão de 10.000,00
        Startup.objects.create(partida=partida, saldo_caixa=10000.00)
        
        return redirect('carregar_jogo', partida_id=partida.id) 
    
    return render(request, 'nova_partida.html')

@login_required
def salvar_jogo(request, partida_id):
    """
    Salva o estado atual e o turno no BDR (Requisito: Salvamento).
    """
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
        
        try:
            startup = partida.startup 
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
        
        # Persiste a escolha no histórico
        HistoricoDecisao.objects.create(
            partida=partida,
            decisao_tomada=decisao_tomada,
            turno=turno_atual
        )
    
    return redirect('dashboard')

@login_required
def carregar_jogo(request, partida_id):
    """
    Restaura o estado da startup e o log de decisões (Requisito: Continuidade).
    """
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
    startup_estado = partida.startup 
    historico_decisoes = partida.decisoes.all().order_by('turno')

    context = {
        'partida': partida,
        'estado_startup': startup_estado,
        'historico_decisoes': historico_decisoes,
    }
    
    return render(request, 'jogo.html', context)

@login_required
def perfil(request):
    partidas_count = Partida.objects.filter(usuario=request.user).count()

    return render(request, 'perfil.html',{
        'usuario': request.user,
        'total_partidas': partidas_count,
    })

@login_required
def historico(request):
    decisoes = HistoricoDecisao.objects.filter(
        partida_usuario = request.user
    ).order_by('-data_decisao')

    return render(request, 'historico.html',{
        'decisoes': decisoes
    })

@login_required
def metricas(request, partida_id):
    partida = get_object_or_404(
        Partida, id=partida_id, usuario=request.user
    )

    startup = partida.startup

    return render(request, 'metricas.html', {
        'partida': partida,
        'startup': startup
    })