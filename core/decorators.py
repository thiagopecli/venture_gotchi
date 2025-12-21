from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def grupo_necessario(nome_do_grupo):
    def in_group(user):
        if user.is_authenticated:
            return user.groups.filter(name=nome_do_grupo).exists()
        return False
    return user_passes_test(in_group, login_url='/login/')

def tipo_usuario_necessario(tipo):
    def check_tipo(user):
        if user.is_authenticated:
            if hasattr(user, 'perfil'):
                return user.perfil.tipo_usuario == tipo
        return False
    return user_passes_test(check_tipo, login_url='/login/')