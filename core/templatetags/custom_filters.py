from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name='moeda_br')
def moeda_br(value):
    """
    Formata valores monetários no padrão brasileiro: R$ 1.234.567,89
    """
    try:
        if value is None:
            return 'R$ 0,00'
        
        # Converter para Decimal se necessário
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Formatar com 2 casas decimais
        formatted = f'{value:,.2f}'
        
        # Substituir separadores: vírgula por ponto (milhar) e ponto por vírgula (decimal)
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f'R$ {formatted}'
    except (ValueError, TypeError, AttributeError, InvalidOperation):
        return 'R$ 0,00'
@register.filter(name='get_field_label')
def get_field_label(form_fields, field_name):
    """
    Obtém o label de um campo do formulário
    """
    if field_name in form_fields:
        return form_fields[field_name].label
    return field_name.replace('_', ' ').title()