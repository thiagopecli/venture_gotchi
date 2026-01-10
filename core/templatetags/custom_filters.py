from django import template
from decimal import Decimal

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
    except (ValueError, TypeError, AttributeError):
        return 'R$ 0,00'
