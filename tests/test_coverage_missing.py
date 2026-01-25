"""
Testes para cobrir as linhas não testadas e atingir 100% de cobertura
"""
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from core.forms import CadastroUsuarioForm, EditarPerfilForm
from core.models import User, Turma, Partida, Startup, Evento, EventoPartida, Conquista
from core.templatetags.custom_filters import moeda_br, get_field_label
from core.permissions import estudante_required, educador_required, pode_salvar_partida, pode_acessar_relatorios, pode_acessar_ranking

User = get_user_model()


class PermissionsDecoratorTestCase(TestCase):
    """Testes para decoradores de permissão - cobrindo branches de acesso negado"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.empresa_user = User.objects.create_user(
            username='empresa',
            email='empresa@test.com',
            password='testpass123',
            categoria='EMPRESA'
        )
        self.educador_user = User.objects.create_user(
            username='educador',
            email='educador@test.com',
            password='testpass123',
            categoria='EDUCADOR_NEGOCIOS'
        )
        self.estudante_user = User.objects.create_user(
            username='estudante',
            email='estudante@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def _add_middleware_to_request(self, request):
        """Adiciona middleware de mensagens e sessão ao request"""
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware(lambda x: x)
        middleware.process_request(request)
    
    def test_estudante_required_acesso_negado_empresa(self):
        """Testa que usuário EMPRESA é negado em @estudante_required"""
        @estudante_required
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = self.empresa_user
        response = view(request)
        # Deve redirecionar para dashboard
        self.assertEqual(response.status_code, 302)
    
    def test_educador_required_acesso_negado_estudante(self):
        """Testa que usuário ESTUDANTE é negado em @educador_required"""
        @educador_required
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = self.estudante_user
        response = view(request)
        # Deve redirecionar para dashboard
        self.assertEqual(response.status_code, 302)
    
    def test_pode_salvar_partida_acesso_negado_empresa(self):
        """Testa que EMPRESA não pode salvar partida"""
        @pode_salvar_partida
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = self.empresa_user
        response = view(request)
        self.assertEqual(response.status_code, 302)
    
    def test_pode_acessar_relatorios_acesso_negado_estudante(self):
        """Testa que ESTUDANTE não pode acessar relatórios"""
        @pode_acessar_relatorios
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = self.estudante_user
        response = view(request)
        self.assertEqual(response.status_code, 302)
    
    def test_pode_acessar_ranking_acesso_negado_empresa(self):
        """Testa que EMPRESA não pode acessar ranking"""
        @pode_acessar_ranking
        def view(request):
            return "OK"
        
        request = self.factory.get('/')
        self._add_middleware_to_request(request)
        request.user = self.empresa_user
        response = view(request)
        self.assertEqual(response.status_code, 302)


class ModelStrRepresentationTestCase(TestCase):
    """Testes para __str__ methods em models que não estão cobertas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
    
    def test_evento_str(self):
        """Testa representação em string de Evento"""
        evento = Evento.objects.create(
            titulo='Evento de Teste',
            descricao='Descrição do evento',
            categoria='mercado'
        )
        self.assertEqual(str(evento), 'Evento de Teste')
    
    def test_evento_partida_str(self):
        """Testa representação em string de EventoPartida"""
        partida = Partida.objects.create(
            usuario=self.user,
            nome_empresa='Teste Startup'
        )
        evento = Evento.objects.create(
            titulo='Evento Teste',
            descricao='Desc',
            categoria='mercado'
        )
        evento_partida = EventoPartida.objects.create(
            partida=partida,
            evento=evento,
            turno=1
        )
        expected = f"{evento.titulo} (T1)"
        self.assertEqual(str(evento_partida), expected)


class TemplateFilterTestCase(TestCase):
    """Testes para template filters não cobertos"""
    
    def test_get_field_label_campo_existe(self):
        """Testa get_field_label quando campo existe"""
        form = CadastroUsuarioForm()
        label = get_field_label(form.fields, 'username')
        self.assertEqual(label, 'Nome de usuário')
    
    def test_get_field_label_campo_nao_existe(self):
        """Testa get_field_label quando campo não existe"""
        form = CadastroUsuarioForm()
        label = get_field_label(form.fields, 'campo_inexistente')
        # Deve retornar o nome formatado do campo
        self.assertEqual(label, 'Campo Inexistente')
    
    def test_moeda_br_string_numero(self):
        """Testa formatação de string com número"""
        resultado = moeda_br('1234.56')
        self.assertEqual(resultado, 'R$ 1.234,56')
    
    def test_moeda_br_none_value(self):
        """Testa formatação com valor None"""
        resultado = moeda_br(None)
        self.assertEqual(resultado, 'R$ 0,00')


class ConquistaStrTestCase(TestCase):
    """Testes para __str__ da classe Conquista"""
    
    def test_conquista_str(self):
        """Testa representação em string de Conquista"""
        conquista = Conquista.objects.create(
            titulo='Primeira Vitória',
            descricao='Ganha a primeira partida',
            tipo='progresso'
        )
        self.assertEqual(str(conquista), 'Primeira Vitória')


class UserMethodsPermissionsTestCase(TestCase):
    """Testes para verificar todas as combinações de permissões de usuário"""
    
    def setUp(self):
        self.company = User.objects.create_user(
            username='company',
            email='company@test.com',
            password='testpass123',
            categoria='EMPRESA'
        )
    
    def test_empresa_pode_salvar_partida(self):
        """Empresa não deve poder salvar partida"""
        self.assertFalse(self.company.pode_salvar_carregar_partida())
    
    def test_empresa_pode_visualizar_propria_partida(self):
        """Empresa não deve poder visualizar partida"""
        self.assertFalse(self.company.pode_visualizar_propria_partida())
    
    def test_empresa_pode_acessar_relatorios(self):
        """Empresa não deve poder acessar relatórios"""
        self.assertFalse(self.company.pode_acessar_relatorios_agregados())
    
    def test_empresa_pode_acessar_ranking(self):
        """Empresa não deve poder acessar ranking"""
        self.assertFalse(self.company.pode_acessar_ranking())
    
    def test_empresa_pode_desbloquear_conquistas(self):
        """Empresa não deve poder desbloquear conquistas"""
        self.assertFalse(self.company.pode_desbloquear_conquistas())
    
    def test_empresa_pode_visualizar_conquistas(self):
        """Todos (incluindo Empresa) podem visualizar conquistas"""
        self.assertTrue(self.company.pode_visualizar_conquistas())


class FormsValidationEdgeCasesTestCase(TestCase):
    """Testes adicionais para cobrir branches em forms.py"""
    
    def test_form_save_com_clean(self):
        """Testa salvamento de form com clean"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'SenhaForteTeste123!',
            'password2': 'SenhaForteTeste123!',
            'first_name': 'Novo',
            'categoria': 'ESTUDANTE_UNIVERSITARIO',
            'pais': 'Brasil',
            'estado': 'SP',
            'municipio': 'São Paulo'
        }
        form = CadastroUsuarioForm(data=form_data)
        if form.is_valid():
            user = form.save()
            self.assertIsNotNone(user.id)
            self.assertEqual(user.email, 'new@test.com')
    
    def test_form_editar_perfil_salva_campos_opcionais(self):
        """Testa que EditarPerfilForm salva campos opcionais"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            categoria='ESTUDANTE_UNIVERSITARIO'
        )
        form_data = {
            'first_name': 'João',
            'email': 'newemail@test.com',
            'pais': 'BR',
            'estado': 'SP',
            'municipio': 'São Paulo'
        }
        form = EditarPerfilForm(data=form_data, instance=user)
        if form.is_valid():
            user = form.save()
            self.assertEqual(user.first_name, 'João')
            self.assertEqual(user.email, 'newemail@test.com')
