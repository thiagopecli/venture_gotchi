"""
Sistema de permissões e decoradores para controle de acesso
"""
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def estudante_required(view_func):
    """
    Decorator que permite acesso apenas para Estudantes/Aspirantes
    (Aluno, Startup PF/PJ)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.is_estudante() or request.user.is_aspirante()):
            messages.error(
                request, 
                'Acesso negado. Esta funcionalidade está disponível apenas para Estudantes/Aspirantes.'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def educador_required(view_func):
    """
    Decorator que permite acesso apenas para Educadores de Negócios
    (Professor, Instituição)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_educador():
            messages.error(
                request, 
                'Acesso negado. Esta funcionalidade está disponível apenas para Educadores.'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def pode_salvar_partida(view_func):
    """
    Decorator que verifica se o usuário pode salvar/carregar partidas
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.pode_salvar_carregar_partida():
            messages.error(
                request, 
                'Você não tem permissão para criar ou gerenciar partidas.'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def pode_acessar_relatorios(view_func):
    """
    Decorator que verifica se o usuário pode acessar relatórios agregados
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.pode_acessar_relatorios_agregados():
            messages.error(
                request, 
                'Acesso negado. Apenas Educadores podem acessar relatórios agregados.'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def pode_acessar_ranking(view_func):
    """
    Decorator que verifica se o usuário pode acessar ranking
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.pode_acessar_ranking():
            messages.error(
                request, 
                'Acesso negado. Apenas Educadores podem acessar o ranking.'
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
