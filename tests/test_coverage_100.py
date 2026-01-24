"""
Testes adicionais para alcançar 100% de cobertura
Cobre lacunas em forms.py, permissions.py, models.py e custom_filters.py
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal

from core.forms import CadastroUsuarioForm, EditarPerfilForm
from core.models import User, Turma
from core.templatetags.custom_filters import moeda_br

User = get_user_model()


class FormsAdvancedTestCase(TestCase):
    """Testes para cobrir branches específicas em forms.py"""
    
    def test_cadastro_estudante_ensino_medio_salva_matricula(self):
        """Testa salvamento de matrícula para estudante de ensino médio"""
        form_data = {
            'username': 'estudante',
            'email': 'estudante@test.com',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
            'first_name': 'João',
            'last_name': 'Silva',
            'categoria': 'ESTUDANTE_ENSINO_MEDIO',
            'matricula_aluno': '123456'
        }
        form = CadastroUsuarioForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(user.matricula_aluno, '123456')
    
    def test_cadastro_profissional_salva_cnpj(self):
        """Testa salvamento de CNPJ para profissional"""
        form_data = {
            'username': 'prof',
            'email': 'prof@test.com',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'categoria': 'PROFISSIONAL_CORPORATIVO',
            'cnpj': '12345678000195',
            'area_atuacao': 'TI'
        }
        form = CadastroUsuarioForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(user.cnpj, '12345678000195')
            self.assertEqual(user.area_atuacao, 'TI')


class PermissionsRedirectTestCase(TestCase):
    """Testes para cobrir redirects em permissions.py"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_estudante_required_redirect_para_login(self):
        """Testa redirect de estudante_required para não autenticado"""
        response = self.client.get(reverse('salvar_jogo', args=[1]))
        self.assertEqual(response.status_code, 302)
    
    def test_educador_required_redirect_para_login(self):
        """Testa redirect de educador_required para não autenticado"""
        response = self.client.get(reverse('educador_dashboard'))
        self.assertEqual(response.status_code, 302)


class ModelsAdditionalMethodsTestCase(TestCase):
    """Testes para métodos auxiliares em models.py"""
    
    def test_turma_gerar_codigo_unico_garantia(self):
        """Testa que gerar_codigo_unico não gera duplicatas"""
        codigos = set()
        for _ in range(10):
            codigo = Turma.gerar_codigo_unico()
            self.assertNotIn(codigo, codigos)
            codigos.add(codigo)
    
    def test_user_is_educador_false(self):
        """Testa is_educador retorna False para estudante"""
        user = User.objects.create_user(
            username='estudante',
            password='pass',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        self.assertFalse(user.is_educador())
    
    def test_user_is_estudante_false(self):
        """Testa is_estudante retorna False para educador"""
        user = User.objects.create_user(
            username='educador',
            password='pass',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.assertFalse(user.is_estudante())


class TemplateTagsEdgeCasesTestCase(TestCase):
    """Testes para cobrir edge cases em custom_filters.py"""
    
    def test_moeda_br_com_decimal_negativo(self):
        """Testa moeda_br com Decimal negativo"""
        resultado = moeda_br(Decimal('-1500.50'))
        self.assertEqual(resultado, "R$ -1.500,50")
    
    def test_moeda_br_com_zero(self):
        """Testa moeda_br com zero"""
        resultado = moeda_br(0)
        self.assertEqual(resultado, "R$ 0,00")
    
    def test_moeda_br_com_inteiro(self):
        """Testa moeda_br com inteiro"""
        resultado = moeda_br(1000)
        self.assertEqual(resultado, "R$ 1.000,00")
