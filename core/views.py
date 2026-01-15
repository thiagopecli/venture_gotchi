from .forms import CadastroUsuarioForm
from .permissions import estudante_required, educador_required, pode_salvar_partida, pode_acessar_relatorios, pode_acessar_ranking
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.messages import get_messages
from decimal import Decimal
from core.services.conquistas import verificar_conquistas_partida, verificar_conquistas_progesso
from .models import User, Partida, Startup, HistoricoDecisao 
from django.db.models import Prefetch

class PaginaLogin(LoginView):
    template_name = 'login.html'

def registro_view(request):
    """
    View unificada para registro usando CadastroUsuarioForm.
    """
   
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            
            return redirect('redirect_handler') 
        else:
            messages.error(request, 'Erro no formulário. Verifique os dados.')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'registro.html', {'form': form})

from .models import ConquistaDesbloqueada, Partida, Startup, HistoricoDecisao 
from django.db.models import Prefetch

def registro_view(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CadastroUsuarioForm()
    
    return render(request, 'registro.html', {'form': form})

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
@pode_salvar_partida
def nova_partida(request):
    """
    Processa o formulário de criação de nova partida e inicializa a startup.
    """
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        saldo_inicial = request.POST.get('saldo_inicial', '50000')
        
        try:
            saldo_inicial = Decimal(saldo_inicial)
            if saldo_inicial < Decimal('0.01'):
                messages.error(request, 'O saldo inicial deve ser de pelo menos R$ 0,01')
                return render(request, 'nova_partida.html')
        except (ValueError, TypeError):
            messages.error(request, 'Saldo inicial inválido. Use apenas números.')
            return render(request, 'nova_partida.html')
        
        partida = Partida.objects.create(
            usuario=request.user,
            nome_empresa=nome_empresa,
            data_inicio=timezone.now(),
        )
        
        Startup.objects.create(partida=partida, saldo_caixa=saldo_inicial)
        
        # Verifica e registra conquistas que dependem da criação da partida
        verificar_conquistas_partida(partida)

        return redirect('carregar_jogo', partida_id=partida.id)
    
    return render(request, 'nova_partida.html')

@login_required
@pode_salvar_partida
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
            
            receita_atual = Decimal(str(startup.receita_mensal))
            saldo_atual = Decimal(str(startup.saldo_caixa)) + receita_atual
            
            if receita_atual > 0:
                messages.info(request, f'💰 Receita mensal de R$ {receita_atual:.2f} adicionada ao caixa!')
            
            custos_decisoes = {
                'Investir em Marketing Agressivo': Decimal('5000.00'),
                'Contratar Engenheiro Sênior': Decimal('8000.00'),
                'Não fazer nada (Economizar)': Decimal('0.00'),
            }
            
            custo = custos_decisoes.get(decisao_tomada, Decimal('0.00'))
            
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
                messages.success(request, '📢 Investimento em marketing realizado! Receita mensal aumentada em R$ 3.000.')
            elif decisao_tomada == 'Contratar Engenheiro Sênior':
                # Engenheiro aumenta valuation, funcionários e receita mensal
                startup.valuation = startup.valuation + Decimal('25000.00')
                startup.receita_mensal = startup.receita_mensal + Decimal('2000.00')
                startup.funcionarios = startup.funcionarios + 1
                messages.success(request, '👨‍💻 Engenheiro contratado! Valuation +R$ 25.000 e receita mensal +R$ 2.000.')
            elif decisao_tomada == 'Não fazer nada (Economizar)':
                messages.info(request, '💰 Você economizou este turno.')
            
            # Atualizar startup
            startup.saldo_caixa = novo_saldo
            startup.turno_atual = startup.turno_atual + 1 
            startup.save()
            
            turno_atual = startup.turno_atual
            
            
            HistoricoDecisao.objects.create(
                partida=partida,
                decisao_tomada=decisao_tomada,
                turno=turno_atual
            )

    
            verificar_conquistas_partida(partida)
            verificar_conquistas_progesso(request.user)
            
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
    from django.db.models import Count, Sum, Max
    
    partidas = Partida.objects.filter(usuario=request.user)
    partidas_count = partidas.count()
    partidas_ativas = partidas.filter(ativa=True).count()
    partidas_finalizadas = partidas.filter(ativa=False).count()
    
    # Conquistas totais
    conquistas_count = ConquistaDesbloqueada.objects.filter(partida__usuario=request.user).count()
    
    # Estatísticas das startups
    stats = Startup.objects.filter(partida__usuario=request.user).aggregate(
        maior_saldo=Max('saldo_caixa'),
        maior_valuation=Max('valuation'),
        maior_turno=Max('turno_atual')
    )
    
    return render(request, 'perfil.html',{
        'usuario': request.user,
        'total_partidas': partidas_count,
        'partidas_ativas': partidas_ativas,
        'partidas_finalizadas': partidas_finalizadas,
        'total_conquistas': conquistas_count,
        'maior_saldo': stats['maior_saldo'] or 0,
        'maior_valuation': stats['maior_valuation'] or 0,
        'maior_turno': stats['maior_turno'] or 0,
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

@login_required
def conquistas(request):
    
    for partida in Partida.objects.filter(usuario=request.user):
        verificar_conquistas_partida(partida)
        verificar_conquistas_progesso(request.user)

    conquistas = (
        ConquistaDesbloqueada.objects
        .select_related('conquista', 'partida', 'partida__startup')
        .filter(partida__usuario=request.user)
    )
    return render(request, 'conquistas.html', {'conquistas': conquistas})

@login_required
@pode_acessar_ranking
def ranking(request):
    """
    Exibe ranking das startups por diferentes critérios.
    Disponível para Estudantes e Educadores.
    """
    from django.db.models import Max, Count, Q
    
    # Determinar critério de ordenação
    criterio = request.GET.get('criterio', 'valuation')
    
    # Buscar todas as startups ativas
    startups = (
        Startup.objects
        .select_related('partida', 'partida__usuario')
        .filter(partida__ativa=True)
    )
    
    # Anotar com informações adicionais
    startups = startups.annotate(
        total_conquistas=Count('partida__conquistas')
    )
    
    # Ordenar baseado no critério
    if criterio == 'valuation':
        startups = startups.order_by('-valuation', '-saldo_caixa')
        titulo = 'Ranking por Valuation'
    elif criterio == 'saldo':
        startups = startups.order_by('-saldo_caixa', '-valuation')
        titulo = 'Ranking por Saldo em Caixa'
    elif criterio == 'turno':
        startups = startups.order_by('-turno_atual', '-valuation')
        titulo = 'Ranking por Turno Alcançado'
    elif criterio == 'conquistas':
        startups = startups.order_by('-total_conquistas', '-valuation')
        titulo = 'Ranking por Conquistas'
    else:
        startups = startups.order_by('-valuation')
        titulo = 'Ranking Geral'
    
    # Limitar aos top 50
    startups = startups[:50]
    
    context = {
        'startups': startups,
        'criterio': criterio,
        'titulo': titulo,
    }
    
    return render(request, 'ranking.html', context)
def redirect_handler(request):
    """Encaminha o usuário baseado na Categoria definida no seu Models"""
    cat = request.user.categoria

    if cat in [User.Categorias.ALUNO, User.Categorias.PROFESSOR]:
        return redirect('dashboard_academico')
    
    elif cat in [User.Categorias.STARTUP_PF, User.Categorias.STARTUP_PJ]:
        return redirect('dashboard_startup')
    
    elif cat in [User.Categorias.EMPRESA, User.Categorias.INSTITUICAO]:
        return redirect('dashboard_corporativo')

    return redirect('home')
