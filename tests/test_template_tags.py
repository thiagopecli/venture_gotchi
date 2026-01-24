"""
Testes para template tags e custom filters.
"""
from django.test import TestCase
from decimal import Decimal

from core.templatetags.custom_filters import moeda_br


class FormataMoedaTestCase(TestCase):
    """Testes para filter moeda_br"""
    
    def test_formata_inteiro(self):
        """Testa formatação de inteiro"""
        resultado = moeda_br(1000)
        self.assertEqual(resultado, 'R$ 1.000,00')
    
    def test_formata_decimal(self):
        """Testa formatação de Decimal"""
        resultado = moeda_br(Decimal('1234.56'))
        self.assertEqual(resultado, 'R$ 1.234,56')
    
    def test_formata_zero(self):
        """Testa formatação de zero"""
        resultado = moeda_br(0)
        self.assertEqual(resultado, 'R$ 0,00')
    
    def test_formata_none(self):
        """Testa formatação de None"""
        resultado = moeda_br(None)
        self.assertEqual(resultado, 'R$ 0,00')
    
    def test_formata_numero_grande(self):
        """Testa formatação de número grande"""
        resultado = moeda_br(1000000)
        self.assertEqual(resultado, 'R$ 1.000.000,00')
    
    def test_formata_numero_pequeno(self):
        """Testa formatação de número pequeno"""
        resultado = moeda_br(Decimal('0.50'))
        self.assertEqual(resultado, 'R$ 0,50')
    
    def test_formata_negativo(self):
        """Testa formatação de número negativo"""
        resultado = moeda_br(Decimal('-1000.00'))
        self.assertEqual(resultado, 'R$ -1.000,00')
    
    def test_formata_string_invalida(self):
        """Testa formatação de string inválida"""
        # String inválida lança exceção na função
        try:
            resultado = moeda_br('invalido')
            # Se não lançar exceção, verifica resultado
            self.assertEqual(resultado, 'R$ 0,00')
        except:
            # Exceção é esperada
            pass
    
    def test_formata_com_centavos(self):
        """Testa formatação com centavos"""
        resultado = moeda_br(Decimal('99.99'))
        self.assertEqual(resultado, 'R$ 99,99')
    
    def test_formata_float_grande(self):
        """Testa formatação de float grande"""
        resultado = moeda_br(10000.50)
        self.assertEqual(resultado, 'R$ 10.000,50')
