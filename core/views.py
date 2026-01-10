from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from decimal import Decimal

class PaginaLogin(LoginView):
    template_name = 'login.html'

def registro(request):
    """
    View para registro de novos usuários.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validações
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'registro.html')
        
        if password1 != password2:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'registro.html')
        
        if len(password1) < 8:
            messages.error(request, 'A senha deve ter pelo menos 8 caracteres.')
            return render(request, 'registro.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return render(request, 'registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'registro.html')
        
        # Criar o usuário
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return render(request, 'registro.html')
    
    return render(request, 'registro.html')

from .models import Partida, Startup, HistoricoDecisao 
from django.db.models import Prefetch

@login_required 
def dashboard(request):
    """
    Lista as partidas existentes do usuário, ordenadas da mais recente.
    """
    partidas = (
        Partida.objects
        .filter(usuario=request.user)
        .order_by('-data_inicio')
    )
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
        
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('50000.00'))
        
        return redirect('carregar_jogo', partida_id=partida.id)
    
    return render(request, 'nova_partida.html')

@login_required
def salvar_jogo(request, partida_id):
    """
    Lógica crítica: Recebe os dados do jogo (POST) e persiste no BDR.
    Valida decisões e aplica efeitos no caixa e métricas.
    """
    if request.method == 'POST':
        partida = get_object_or_404(
            Partida.objects.select_related('startup'),
            id=partida_id,
            usuario=request.user
        )
        
        try:
            startup = partida.startup
            decisao_tomada = request.POST.get('decisao', 'Decisão não especificada.')
            
            # Custos das decisões
            custos_decisoes = {
                'Investir em Marketing Agressivo': Decimal('5000.00'),
                'Contratar Engenheiro Sênior': Decimal('8000.00'),
                'Não fazer nada (Economizar)': Decimal('0.00'),
            }
            
            # Obter custo da decisão
            custo = custos_decisoes.get(decisao_tomada, Decimal('0.00'))
            saldo_atual = Decimal(str(startup.saldo_caixa))
            
            # Validar se tem saldo suficiente
            if saldo_atual < custo:
                messages.error(
                    request, 
                    f'❌ Saldo insuficiente! Você tem R$ {saldo_atual:.2f} mas precisa de R$ {custo:.2f} para {decisao_tomada}.'
                )
                return redirect('carregar_jogo', partida_id=partida.id)
            
            # Aplicar custos e efeitos
            novo_saldo = saldo_atual - custo
            
            if decisao_tomada == 'Investir em Marketing Agressivo':
                # Marketing aumenta receita mensal
                startup.receita_mensal = startup.receita_mensal + Decimal('3000.00')
                messages.success(request, '📢 Investimento em marketing realizado! Receita aumentada.')
            elif decisao_tomada == 'Contratar Engenheiro Sênior':
                # Engenheiro aumenta valuation e funcionários
                startup.valuation = startup.valuation + Decimal('25000.00')
                startup.funcionarios = startup.funcionarios + 1
                messages.success(request, '👨‍💻 Engenheiro contratado! Valuation aumentado.')
            elif decisao_tomada == 'Não fazer nada (Economizar)':
                messages.info(request, '💰 Você economizou este turno.')
            
            # Atualizar startup
            startup.saldo_caixa = novo_saldo
            startup.turno_atual = startup.turno_atual + 1 
            startup.save()
            
            turno_atual = startup.turno_atual
            
            # Registrar decisão no histórico
            HistoricoDecisao.objects.create(
                partida=partida,
                decisao_tomada=decisao_tomada,
                turno=turno_atual
            )
            
        except Startup.DoesNotExist:
            messages.error(request, 'Erro: Startup não encontrada.')
            return redirect('dashboard')
    
    return redirect('carregar_jogo', partida_id=partida_id)

@login_required
def carregar_jogo(request, partida_id):
    """
    Busca os dados no BDR e prepara o contexto para restaurar o estado do jogo.
    """
    partida = get_object_or_404(
        Partida.objects.select_related('startup').prefetch_related(
            Prefetch(
                'decisoes',
                queryset=HistoricoDecisao.objects.order_by('turno')
            )
        ),
        id=partida_id,
        usuario=request.user,
    )

    startup_estado = partida.startup
    historico_decisoes = partida.decisoes.all()

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
    decisoes = (
        HistoricoDecisao.objects
        .select_related('partida')
        .filter(partida__usuario=request.user)
        .order_by('-data_decisao')
    )

    return render(request, 'historico.html',{
        'decisoes': decisoes
    })

@login_required
def metricas(request, partida_id):
    partida = get_object_or_404(
        Partida.objects.select_related('startup'),
        id=partida_id,
        usuario=request.user
    )

    startup = partida.startup

    return render(request, 'metricas.html', {
        'partida': partida,
        'startup': startup
    })