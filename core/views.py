from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm # Adicionado para o registro

# --- CLASSES DE AUTENTICAÇÃO ---
class PaginaLogin(LoginView):
    template_name = 'login.html'

# --- IMPORTAÇÃO DE MODELOS ---
from .models import Partida, Startup, HistoricoDecisao 

# --- VIEWS PÚBLICAS (Faltavam no seu código) ---

def index(request):
    """Página inicial do projeto"""
    return render(request, 'index.html')

def registrar(request):
    """Lógica de criação de novo usuário"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})

# --- GESTÃO DE PARTIDAS (Seu código com correções) ---

@login_required 
def dashboard(request):
    """Lista as partidas existentes do usuário"""
    partidas = Partida.objects.filter(usuario=request.user).order_by('-data_inicio')
    context = {'partidas': partidas}
    return render(request, 'dashboard.html', context) 

@login_required
def nova_partida(request):
    """Inicializa a startup com saldo de 10.000,00"""
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        Startup.objects.create(partida=partida, saldo_caixa=10000.00)
        return redirect('carregar_jogo', partida_id=partida.id)
    return render(request, 'nova_partida.html')

@login_required
def salvar_jogo(request, partida_id):
    """Persiste os dados do jogo no BDR"""
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
        HistoricoDecisao.objects.create(
            partida=partida,
            decisao_tomada=decisao_tomada,
            turno=turno_atual
        )
    return redirect('dashboard')

@login_required
def carregar_jogo(request, partida_id):
    """Prepara o contexto para restaurar o estado do jogo"""
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
    # Correção: O filtro correto é através da FK 'partida'
    decisoes = HistoricoDecisao.objects.filter(
        partida__usuario=request.user
    ).order_by('-data_hora') # Nome do campo corrigido conforme seu modelo

    return render(request, 'historico.html', {'decisoes': decisoes})

@login_required
def metricas(request, partida_id):
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
    startup = partida.startup
    return render(request, 'metricas.html', {
        'partida': partida,
        'startup': startup
    })