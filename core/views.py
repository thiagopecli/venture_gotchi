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
from .models import User, Partida, Startup, HistoricoDecisao, Turma
from django.db.models import Prefetch
from .forms import EditarPerfilForm
from django.db.models import Avg, Max, Count, Sum
from django.core.exceptions import PermissionDenied

def formatar_moeda_br(valor):
    """
    Formata um valor numérico para o padrão monetário brasileiro: R$ 1.234.567,89
    """
    try:
        if valor is None:
            return 'R$ 0,00'
        
        # Converter para Decimal se necessário
        if isinstance(valor, (int, float)):
            valor = Decimal(str(valor))
        elif not isinstance(valor, Decimal):
            valor = Decimal(str(valor))
        
        # Formatar com 2 casas decimais
        formatted = f'{valor:,.2f}'
        
        # Substituir separadores: vírgula por ponto (milhar) e ponto por vírgula (decimal)
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f'R$ {formatted}'
    except (ValueError, TypeError, AttributeError):
        return 'R$ 0,00'

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

@login_required 
def dashboard(request):
    """
    Lista as partidas existentes do usuário, ordenadas da mais recente.
    Redireciona educadores para o painel específico deles.
    """
    # Redirecionar educadores para o dashboard específico
    if request.user.is_educador():
        return redirect('educador_dashboard')
    
    partidas = (
        Partida.objects
        .filter(usuario=request.user)
        .order_by('-data_inicio')
    )
    
    # Garantir que os valores booleanos sejam passados corretamente
    context = {
        'partidas': partidas,
        'pode_salvar_carregar': request.user.pode_salvar_carregar_partida(),
        'is_estudante': request.user.is_estudante(),
        'is_educador': request.user.is_educador(),
        'is_aspirante': request.user.is_aspirante(),
        'is_profissional': request.user.is_profissional(),
    }
    
    return render(request, 'dashboard.html', context) 

@login_required
@pode_salvar_partida
def nova_partida(request):
    """
    Processa o formulário de criação de nova partida e inicializa a startup.
    """
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa', 'Nova Startup')
        # Saldo inicial fixo: R$ 30.000,00
        saldo_inicial = Decimal('30000.00')
        
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
            
            # Impede novos envios se a partida já foi finalizada (Game Over ou Vitória)
            if not partida.ativa:
                messages.error(request, 'Partida encerrada. Não é possível realizar novas ações.')
                return redirect('carregar_jogo', partida_id=partida.id)
            
            decisao_tomada = request.POST.get('decisao', 'Decisão não especificada.')
            
            # Cálculo de Fluxo de Caixa (Saldo anterior + Receita do turno)
            receita_atual = Decimal(str(startup.receita_mensal))
            saldo_atual = Decimal(str(startup.saldo_caixa)) + receita_atual
            
            # Dicionário de Custos
            custos_decisoes = {
                'Investir em Marketing Agressivo': Decimal('5000.00'),
                'Contratar Engenheiro Sênior': Decimal('8000.00'),
                'Não fazer nada (Economizar)': Decimal('0.00'),
            }
            
            custo = custos_decisoes.get(decisao_tomada, Decimal('0.00'))
            
            # Validar se tem saldo suficiente antes de processar
            if saldo_atual < custo:
                messages.error(
                    request, 
                    f'Saldo insuficiente. Disponível: {formatar_moeda_br(saldo_atual)} | Necessário: {formatar_moeda_br(custo)}'
                )
                return redirect('carregar_jogo', partida_id=partida.id)
            
            # Aplicar custos
            novo_saldo = saldo_atual - custo
            
            # Efeitos das Decisões
            if decisao_tomada == 'Investir em Marketing Agressivo':
                startup.receita_mensal += Decimal('3000.00')
                messages.success(request, 'Investimento em Marketing concluído. Receita aumentada.')
                
            elif decisao_tomada == 'Contratar Engenheiro Sênior':
                startup.valuation += Decimal('25000.00')
                startup.receita_mensal += Decimal('2000.00')
                startup.funcionarios += 1
                messages.success(request, 'Novo Engenheiro Sênior integrado à equipe.')
                
            elif decisao_tomada == 'Não fazer nada (Economizar)':
                messages.info(request, 'Turno finalizado com foco em preservação de capital.')
            
            # Persistência de Dados
            startup.saldo_caixa = novo_saldo
            startup.turno_atual += 1 
            startup.save()
            
            # Registrar no Histórico
            HistoricoDecisao.objects.create(
                partida=partida,
                decisao_tomada=decisao_tomada,
                turno=startup.turno_atual
            )

            # Sistema de Conquistas
            verificar_conquistas_partida(partida)
            novas_conquistas = verificar_conquistas_progesso(request.user, partida_especifica=partida)
            
            # Adicionar conquistas desbloqueadas às mensagens
            for conquista in novas_conquistas:
                messages.success(
                    request, 
                    f'🏆 Conquista Desbloqueada: {conquista.titulo}! +{conquista.pontos} pontos',
                    extra_tags='conquista'
                )
            
        except Startup.DoesNotExist:
            messages.error(request, 'Erro técnico: Startup não vinculada a esta partida.')
            return redirect('dashboard')
    
    return redirect('carregar_jogo', partida_id=partida_id)

@login_required
@estudante_required
def carregar_jogo(request, partida_id):
    partida = get_object_or_404(
        Partida.objects.select_related('startup').prefetch_related(
            Prefetch('decisoes', queryset=HistoricoDecisao.objects.order_by('-turno'))
        ),
        id=partida_id,
        usuario=request.user,
    )

    startup_estado = partida.startup
    historico_decisoes = partida.decisoes.all()

  
    game_over = startup_estado.saldo_caixa <= 0
    
    meta_vitoria = Decimal('1000000.00')
    vitoria = startup_estado.valuation >= meta_vitoria

    
    if (game_over or vitoria) and partida.ativa:
        partida.ativa = False
        partida.save()

    context = {
        'partida': partida,
        'estado_startup': startup_estado,
        'historico_decisoes': historico_decisoes,
        'game_over': game_over, 
        'vitoria': vitoria,     
    }
    
    return render(request, 'jogo.html', context)

@login_required
@estudante_required
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
@estudante_required
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

@estudante_required
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
@estudante_required

@login_required
def conquistas(request):
    """
    Lista as conquistas desbloqueadas do usuário.
    Apenas garante que as conquistas existem, sem reprocessar tudo.
    """
    from core.services.conquistas import _garantir_conquistas_existem
    from itertools import groupby
    
    # Apenas garante que as conquistas base existem no sistema
    _garantir_conquistas_existem()
    
    # Busca as conquistas já desbloqueadas
    conquistas = (
        ConquistaDesbloqueada.objects
        .select_related('conquista', 'partida', 'partida__startup')
        .filter(partida__usuario=request.user)
        .order_by('partida__nome_empresa', '-desbloqueada_em')
    )
    
    # Agrupar por empresa e calcular pontos
    conquistas_por_empresa = []
    conquistas_list = list(conquistas)
    
    for empresa_nome, grupo in groupby(conquistas_list, key=lambda x: x.partida.nome_empresa):
        grupo_list = list(grupo)
        pontos_totais = sum(conquista.conquista.pontos for conquista in grupo_list)
        conquistas_por_empresa.append({
            'empresa': empresa_nome,
            'conquistas': grupo_list,
            'pontos_totais': pontos_totais
        })
    
    return render(request, 'conquistas.html', {'conquistas_por_empresa': conquistas_por_empresa})

@login_required
@pode_acessar_ranking
def ranking(request):
    """
    Exibe ranking das startups com filtro de turma para Educadores e filtros regionais.
    """
    from django.db.models import Max, Count, Q, Sum
    
    # 1. Captura parâmetros
    criterio = request.GET.get('criterio', 'valuation')
    codigo_turma = request.GET.get('codigo_turma', '').strip()
    filtro_pais = request.GET.get('pais', '').strip()
    filtro_estado = request.GET.get('estado', '').strip()
    filtro_municipio = request.GET.get('municipio', '').strip()
    
    # 2. Queryset Base (Apenas startups ativas)
    startups = (
        Startup.objects
        .select_related('partida', 'partida__usuario')
        .filter(partida__ativa=True)
    )
    
    # 3. Filtro por categoria do usuário
    # Estudantes veem apenas startups de outros estudantes
    # Educadores veem todas as startups
    if request.user.categoria == User.Categorias.ESTUDANTE_UNIVERSITARIO:
        startups = startups.filter(partida__usuario__categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO)
    
    # 4. Lógica de Filtro por Turma (Exclusivo Educador/Admin)
    # Verifica se é educador para permitir o filtro
    is_educador = request.user.categoria == User.Categorias.EDUCADOR_NEGOCIOS or request.user.is_superuser
    
    if is_educador and codigo_turma:
        # Filtra pelo campo codigo_turma do Usuário dono da partida
        startups = startups.filter(partida__usuario__codigo_turma__iexact=codigo_turma)
    
    # 4.5. Filtros Regionais
    if filtro_pais:
        startups = startups.filter(partida__usuario__pais__iexact=filtro_pais)
    if filtro_estado:
        startups = startups.filter(partida__usuario__estado__iexact=filtro_estado)
    if filtro_municipio:
        startups = startups.filter(partida__usuario__municipio__icontains=filtro_municipio)

    # 5. Anotações
    startups = startups.annotate(
        total_conquistas=Count('partida__conquistas'),
        pontuacao_conquistas=Sum('partida__conquistas__conquista__pontos')
    )
    
    # 6. Ordenação
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
    
    # Obter listas únicas para os filtros
    paises_disponiveis = User.objects.filter(partidas__ativa=True).values_list('pais', flat=True).distinct().order_by('pais')
    estados_disponiveis = User.objects.filter(partidas__ativa=True).values_list('estado', flat=True).distinct().order_by('estado')
    
    context = {
        'startups': startups,
        'criterio': criterio,
        'titulo': titulo,
        'is_educador': is_educador, 
        'filtro_turma': codigo_turma,
        'filtro_pais': filtro_pais,
        'filtro_estado': filtro_estado,
        'filtro_municipio': filtro_municipio,
        'paises_disponiveis': [p for p in paises_disponiveis if p],
        'estados_disponiveis': [e for e in estados_disponiveis if e],
    }
    
    return render(request, 'ranking.html', context)

def redirect_handler(request):
    """Encaminha o usuário baseado na Categoria definida no seu Models"""
    cat = request.user.categoria

    if cat == User.Categorias.ESTUDANTE_UNIVERSITARIO:
        return redirect('dashboard')  # ou algum dashboard específico
    
    elif cat == User.Categorias.ASPIRANTE_EMPREENDEDOR:
        return redirect('dashboard')
    
    elif cat == User.Categorias.EDUCADOR_NEGOCIOS:
        return redirect('educador_dashboard')
    
    elif cat == User.Categorias.PROFISSIONAL_CORPORATIVO:
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os campos.')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'editar_perfil.html', {'form': form})

def educador_only(view_func):
    """Decorator para garantir que apenas Educadores acessem"""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.categoria != User.Categorias.EDUCADOR_NEGOCIOS and not request.user.is_superuser:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@educador_only
def educador_dashboard(request):
    # Buscar todas as turmas do educador
    turmas_educador = Turma.objects.filter(educador=request.user, ativa=True)
    
    context = {
        'turmas_educador': turmas_educador,
    }

    return render(request, 'educador_dashboard.html', context)

@login_required
@educador_required
def educador_perfil(request):
    """
    Exibe o perfil do educador com estatísticas de suas turmas e alunos.
    """
    # Buscar todas as turmas do educador
    turmas = Turma.objects.filter(educador=request.user, ativa=True)
    turmas_ativas = turmas.count()
    turmas_total = turmas.count()
    
    # Contar alunos únicos em todas as turmas
    alunos = User.objects.filter(
        categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO,
        codigo_turma__in=turmas.values('codigo')
    ).distinct()
    total_alunos = alunos.count()
    
    # Buscar partidas ativas dos alunos
    partidas = Partida.objects.filter(
        usuario__in=alunos,
        ativa=True
    )
    partidas_ativas = partidas.count()
    
    # Estatísticas agregadas das startups dos alunos
    stats = Startup.objects.filter(partida__usuario__in=alunos).aggregate(
        media_valuation=Avg('valuation'),
        media_saldo=Avg('saldo_caixa'),
        maior_valuation=Max('valuation'),
        maior_saldo=Max('saldo_caixa')
    )
    
    return render(request, 'educador_perfil.html', {
        'usuario': request.user,
        'total_turmas': turmas_total,
        'turmas_ativas': turmas_ativas,
        'total_alunos': total_alunos,
        'partidas_ativas': partidas_ativas,
        'media_valuation': stats['media_valuation'] or 0,
        'media_saldo': stats['media_saldo'] or 0,
        'maior_valuation': stats['maior_valuation'] or 0,
        'maior_saldo': stats['maior_saldo'] or 0,
    })

@login_required
@educador_required
def educador_editar_perfil(request):
    """
    Permite que o educador edite seu perfil.
    """
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('educador_perfil')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os campos.')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'editar_perfil.html', {'form': form})

@login_required
@educador_only
def criar_turma(request):
    """
    Cria uma nova turma para o educador com código único gerado automaticamente.
    """
    if request.method == 'POST':
        nome_turma = request.POST.get('nome_turma', '').strip()
        descricao_turma = request.POST.get('descricao_turma', '').strip()
        
        if not nome_turma:
            messages.error(request, 'O nome da turma é obrigatório.')
            return redirect('educador_dashboard')
        
        # Gerar código único
        codigo = Turma.gerar_codigo_unico()
        
        # Criar turma
        turma = Turma.objects.create(
            codigo=codigo,
            nome=nome_turma,
            descricao=descricao_turma,
            educador=request.user
        )
        
        messages.success(request, f'Turma "{nome_turma}" criada com sucesso! Código: {codigo}')
        return redirect('educador_dashboard')
    
    return redirect('educador_dashboard')

@login_required
@educador_only
@login_required
@educador_only
def analise_turma(request, codigo_turma):
    """
    Exibe análise detalhada de uma turma específica.
    """
    turma = get_object_or_404(Turma, codigo__iexact=codigo_turma)
    
    # Buscar partidas e alunos dessa turma (case-insensitive)
    partidas = Partida.objects.filter(ativa=True, usuario__codigo_turma__iexact=turma.codigo)
    users_alunos = User.objects.filter(categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO, codigo_turma__iexact=turma.codigo)
    
    # Calcular KPIs
    kpis = Startup.objects.filter(partida__in=partidas).aggregate(
        media_valuation=Avg('valuation'),
        media_caixa=Avg('saldo_caixa'),
        maior_valuation=Max('valuation'),
        total_startups=Count('partida'),
        media_turno=Avg('turno_atual')
    )
    
    # Ranking da turma
    ranking = (
        Startup.objects
        .select_related('partida', 'partida__usuario')
        .filter(partida__in=partidas)
        .order_by('-valuation')[:20]
    )
    
    context = {
        'turma': turma,
        'kpis': kpis,
        'ranking': ranking,
        'total_alunos': users_alunos.count(),
        'turno_medio': int(kpis.get('media_turno') or 0),
    }
    
    return render(request, 'analise_turma.html', context)

@login_required
@educador_only
def ranking_turmas(request):
    """
    Exibe ranking com dados agregados de TODAS as turmas do sistema.
    """
    # Buscar TODAS as turmas que têm alunos ativos
    turmas = Turma.objects.filter(ativa=True).order_by('-data_criacao')
    
    turmas_dados = []
    for turma in turmas:
        partidas = Partida.objects.filter(ativa=True, usuario__codigo_turma__iexact=turma.codigo)
        users_alunos = User.objects.filter(categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO, codigo_turma__iexact=turma.codigo)
        
        kpis = Startup.objects.filter(partida__in=partidas).aggregate(
            media_valuation=Avg('valuation'),
            maior_valuation=Max('valuation'),
            total_startups=Count('partida')
        )
        
        turmas_dados.append({
            'turma': turma,
            'total_alunos': users_alunos.count(),
            'startups_ativas': kpis.get('total_startups') or 0,
            'media_valuation': kpis.get('media_valuation') or 0,
            'maior_valuation': kpis.get('maior_valuation') or 0,
        })
    
    context = {
        'turmas_dados': turmas_dados,
    }
    
    return render(request, 'ranking_turmas.html', context)

@login_required
@educador_only
def metricas_turmas(request):
    """
    Exibe análise geral agregada de TODAS as turmas do sistema.
    """
    # Buscar TODAS as turmas ativas
    turmas = Turma.objects.filter(ativa=True).order_by('-data_criacao')
    
    # Buscar todos os dados das turmas
    turmas_dados = []
    total_alunos = 0
    total_startups = 0
    total_valuation = 0
    max_valuation = 0
    
    for turma in turmas:
        partidas = Partida.objects.filter(ativa=True, usuario__codigo_turma__iexact=turma.codigo)
        users_alunos = User.objects.filter(categoria=User.Categorias.ESTUDANTE_UNIVERSITARIO, codigo_turma__iexact=turma.codigo)
        
        kpis = Startup.objects.filter(partida__in=partidas).aggregate(
            media_valuation=Avg('valuation'),
            maior_valuation=Max('valuation'),
            total_startups=Count('partida'),
            media_caixa=Avg('saldo_caixa')
        )
        
        alunos_count = users_alunos.count()
        startups_count = kpis.get('total_startups') or 0
        media_val = kpis.get('media_valuation') or 0
        maior_val = kpis.get('maior_valuation') or 0
        
        total_alunos += alunos_count
        total_startups += startups_count
        total_valuation += media_val
        
        if maior_val > max_valuation:
            max_valuation = maior_val
        
        turmas_dados.append({
            'turma': turma,
            'total_alunos': alunos_count,
            'startups_ativas': startups_count,
            'media_valuation': media_val,
            'maior_valuation': maior_val,
            'media_caixa': kpis.get('media_caixa') or 0,
        })
    
    # Calcular médias gerais
    media_valuation_geral = total_valuation / len(turmas) if turmas.count() > 0 else 0
    
    context = {
        'turmas_dados': turmas_dados,
        'total_turmas': turmas.count(),
        'total_alunos': total_alunos,
        'total_startups': total_startups,
        'media_valuation': media_valuation_geral,
        'media_caixa': sum(t['media_caixa'] for t in turmas_dados) / len(turmas_dados) if turmas_dados else 0,
        'maior_valuation': max_valuation,
    }
    
    return render(request, 'metricas_turmas.html', context)

import random
import string

@login_required
@educador_required
def gerar_codigo_turma(request):
    """
    Gera um código único de turma para educadores.
    """
    if request.method == 'POST':
        while True:
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            numeros = ''.join(random.choices(string.digits, k=3))
            codigo = f"{letras}-{numeros}"
            
            
            if not User.objects.filter(codigo_turma=codigo).exists():
                break
        
        
        messages.success(request, f'Código de turma gerado: {codigo}')
        return redirect('dashboard')
    
    return redirect('dashboard')