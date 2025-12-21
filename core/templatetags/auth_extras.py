from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user.is_authenticated:
        return user.groups.filter(name=group_name).exists()
    return False

@register.filter(name='is_tipo_usuario')
def is_tipo_usuario(user, tipo):
    if user.is_authenticated and hasattr(user, 'perfil'):
        return user.perfil.tipo_usuario == tipo
    return False