from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
# Importação dos novos modelos para persistência de dados
from .models import (
    Partida, Startup, HistoricoDecisao, 
    Fundador, EventoPartida, ConquistaDesbloqueada
)

# --- CLASSES DE AUTENTICAÇÃO ---
class PaginaLogin(LoginView):
    template_name = 'login.html'

# --- VIEWS PÚBLICAS ---

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

# --- GESTÃO DE PARTIDAS ---

@login_required 
def dashboard(request):
    """Lista as partidas existentes do usuário"""
    partidas = Partida.objects.filter(usuario=request.user).order_by('-data_inicio')
    context = {'partidas': partidas}
    return render(request, 'dashboard.html', context) 

@login_required
def nova_partida(request):
    """Inicializa a partida, a startup e o fundador com dados iniciais"""
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        
        # 1. Cria a Partida
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        
        # 2. Cria a Startup vinculada (com os campos recriados)
        Startup.objects.create(
            partida=partida, 
            nome=nome_empresa,
            saldo_caixa=10000.00,
            receita_mensal=0.00,
            valuation=10000.00,
            funcionarios=1
        )

        # 3. Cria o Fundador inicial para a partida
        Fundador.objects.create(
            partida=partida,
            nome=request.user.username,
            experiencia='tecnologia'
        )
        
        return redirect('carregar_jogo', partida_id=partida.id)
    return render(request, 'nova_partida.html')

@login_required
def salvar_jogo(request, partida_id):
    """Persiste os dados detalhados do jogo no BDR"""
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
        try:
            startup = partida.startup 
            # Atualiza métricas financeiras enviadas pelo formulário
            startup.saldo_caixa = float(request.POST.get('saldo_atual', startup.saldo_caixa))
            startup.receita_mensal = float(request.POST.get('receita', startup.receita_mensal))
            
            startup.turno_atual += 1 
            startup.save()
            turno_atual = startup.turno_atual
        except (Startup.DoesNotExist, ValueError, TypeError):
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
    """Restaura o estado completo do jogo"""
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
    
    context = {
        'partida': partida,
        'estado_startup': partida.startup,
        'fundador': getattr(partida, 'fundador', None),
        'historico_decisoes': partida.decisoes.all().order_by('turno'),
    }
    return render(request, 'jogo.html', context)

@login_required
def metricas(request, partida_id):
    """Exibe métricas, eventos e conquistas da partida"""
    partida = get_object_or_404(Partida, id=partida_id, usuario=request.user)
    
    context = {
        'partida': partida,
        'startup': partida.startup,
        'fundador': getattr(partida, 'fundador', None),
        'eventos': EventoPartida.objects.filter(partida=partida),
        'conquistas': ConquistaDesbloqueada.objects.filter(partida=partida),
    }
    return render(request, 'metricas.html', context)

@login_required
def perfil(request):
    partidas_count = Partida.objects.filter(usuario=request.user).count()
    return render(request, 'perfil.html',{
        'usuario': request.user,
        'total_partidas': partidas_count,
    })

@login_required
def historico(request):
    """Exibe o log de decisões de todas as partidas do usuário"""
    decisoes = HistoricoDecisao.objects.filter(
        partida__usuario=request.user
    ).order_by('-data_decisao') # Verifique se no model é data_decisao ou data_hora

    return render(request, 'historico.html', {'decisoes': decisoes})