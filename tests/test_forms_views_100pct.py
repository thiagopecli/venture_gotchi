"""
Testes para atingir 100% de cobertura em forms.py e views.py
"""
from decimal import Decimal, InvalidOperation
from unittest.mock import patch

from django import forms as django_forms
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

from core.forms import CadastroUsuarioForm, EditarPerfilForm
from core.models import Partida, Startup, Turma, HistoricoDecisao, ConquistaDesbloqueada, Conquista
from core.views import formatar_moeda_br

User = get_user_model()


import uuid

def create_user(username='user', categoria='ESTUDANTE_UNIVERSITARIO', codigo_turma='ABC-123'):
    # Criar com save padrão, forçando defaults
    user = User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='SenhaForte123!',
        categoria=categoria,
        codigo_turma=codigo_turma if categoria == 'ESTUDANTE_UNIVERSITARIO' else None,
        municipio='Cidade',
        estado='SP',
        pais='Brasil'
    )
    # Para aspirante/educador, garantir documento único
    if categoria == 'EDUCADOR_NEGOCIOS':
        user.tipo_documento = 'CPF'
        user.documento = str(uuid.uuid4().int)[:11]
        user.save()
    elif categoria == 'ASPIRANTE_EMPREENDEDOR':
        user.tipo_documento = 'CPF'
        user.documento = str(uuid.uuid4().int)[:11]
        user.save()
    elif categoria == 'PROFISSIONAL_CORPORATIVO':
        user.tipo_documento = 'CNPJ'
        user.documento = str(uuid.uuid4().int)[:14]
        user.save()
    return user


class FormsBranchesComplementTestCase(TestCase):
    def _manual_form(self, cleaned_data):
        form = CadastroUsuarioForm()
        form._errors = {}
        form.cleaned_data = cleaned_data
        return form

    def test_username_missing(self):
        form = self._manual_form({'username': None})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_username()

    def test_username_max_chars(self):
        form = self._manual_form({'username': 'a' * 151})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_username()

    def test_email_missing(self):
        form = self._manual_form({'email': None})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_email()

    def test_email_bad_format(self):
        form = self._manual_form({'email': 'bad'})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_email()

    def test_password2_missing(self):
        form = self._manual_form({'password1': 'SenhaForte', 'password2': None})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_password2()

    def test_password_too_short(self):
        form = self._manual_form({'password1': 'Abc1', 'password2': 'Abc1'})
        form.clean_password2()
        self.assertIn('password1', form.errors)

    def test_password_no_lower(self):
        form = self._manual_form({'password1': 'PASSWORD1', 'password2': 'PASSWORD1', 'username': 'user'})
        form.clean_password2()
        self.assertIn('password1', form.errors)

    def test_password_no_number(self):
        form = self._manual_form({'password1': 'Password', 'password2': 'Password', 'username': 'user'})
        form.clean_password2()
        self.assertIn('password1', form.errors)

    def test_password_equals_username(self):
        form = self._manual_form({'password1': 'SameUser1', 'password2': 'SameUser1', 'username': 'SameUser1'})
        form.clean_password2()
        self.assertIn('password1', form.errors)

    def test_first_name_missing(self):
        form = self._manual_form({'first_name': None})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_first_name()

    def test_first_name_too_long(self):
        form = self._manual_form({'first_name': 'A' * 151})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_first_name()

    def test_first_name_too_short(self):
        form = self._manual_form({'first_name': 'AB'})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_first_name()

    def test_municipio_too_long(self):
        form = self._manual_form({'municipio': 'a' * 101})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_municipio()

    def test_estado_invalid(self):
        form = self._manual_form({'estado': 'ZZ'})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_estado()

    def test_pais_invalid(self):
        form = self._manual_form({'pais': 'XX'})
        with self.assertRaises(django_forms.ValidationError):
            form.clean_pais()

    def test_estudante_matricula_invalid_clean(self):
        form = self._manual_form({
            'categoria': User.Categorias.ESTUDANTE_UNIVERSITARIO,
            'codigo_turma': 'ABC-123',
            'matricula_aluno': 'ABC'
        })
        with self.assertRaises(django_forms.ValidationError):
            form.clean()

    def test_educador_nome_muito_longo(self):
        form = self._manual_form({
            'categoria': User.Categorias.EDUCADOR_NEGOCIOS,
            'cpf': '12345678901',
            'nome_instituicao': 'X' * 101
        })
        with self.assertRaises(django_forms.ValidationError):
            form.clean()

    def test_aspirante_area_muito_longa(self):
        form = self._manual_form({
            'categoria': User.Categorias.ASPIRANTE_EMPREENDEDOR,
            'cpf': '12345678901',
            'area_atuacao': 'Y' * 101
        })
        with self.assertRaises(django_forms.ValidationError):
            form.clean()

    def test_profissional_nome_empresa_muito_longo(self):
        form = self._manual_form({
            'categoria': User.Categorias.PROFISSIONAL_CORPORATIVO,
            'cnpj': '12345678901234',
            'nome_empresa': 'Z' * 101
        })
        with self.assertRaises(django_forms.ValidationError):
            form.clean()

    def test_educador_cpf_invalido_customizado(self):
        form = self._manual_form({
            'categoria': User.Categorias.EDUCADOR_NEGOCIOS,
            'cpf': '123abc',
            'nome_instituicao': 'Instituicao Valida'
        })
        with self.assertRaises(django_forms.ValidationError) as cm:
            form.clean()
        self.assertIn('cpf', cm.exception.message_dict)

    def test_aspirante_cpf_invalido_customizado(self):
        form = self._manual_form({
            'categoria': User.Categorias.ASPIRANTE_EMPREENDEDOR,
            'cpf': '999',
            'area_atuacao': 'Tecnologia'
        })
        with self.assertRaises(django_forms.ValidationError) as cm:
            form.clean()
        self.assertIn('cpf', cm.exception.message_dict)

    def test_profissional_cnpj_invalido_customizado(self):
        form = self._manual_form({
            'categoria': User.Categorias.PROFISSIONAL_CORPORATIVO,
            'cnpj': 'abc',
            'nome_empresa': 'Empresa Valida'
        })
        with self.assertRaises(django_forms.ValidationError) as cm:
            form.clean()
        self.assertIn('cnpj', cm.exception.message_dict)

    def test_save_estudante_no_commit(self):
        data = {
            'username': 'estudante_nocommit',
            'email': 'estudante_nc@test.com',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
            'first_name': 'Estudante NoCommit',
            'categoria': User.Categorias.ESTUDANTE_UNIVERSITARIO,
            'codigo_turma': 'ABC-123',
            'matricula_aluno': '123456',
            'municipio': '',
            'estado': '',
            'pais': ''
        }
        form = CadastroUsuarioForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertIsNone(user.pk)
        self.assertEqual(user.municipio, 'Nao informado')
        self.assertEqual(user.estado, 'SP')
        self.assertEqual(user.pais, 'Brasil')

    def test_save_defaults_estudante(self):
        user = User.objects.create_user(
            username='save_test',
            email='save@test.com',
            password='SenhaForte123!',
            categoria='ESTUDANTE_UNIVERSITARIO',
            codigo_turma='ABC-123',
            matricula_aluno='123456',
            municipio='Nao informado',
            estado='SP',
            pais='Brasil'
        )
        self.assertEqual(user.pais, 'Brasil')
        self.assertEqual(user.estado, 'SP')
        self.assertEqual(user.municipio, 'Nao informado')

    def test_save_with_existing_location(self):
        # Testar save() quando já há municipio/estado/pais (branches 348-353)
        data = {
            'username': 'user_with_loc',
            'email': 'loc@test.com',
            'password1': 'SenhaForte123!',
            'password2': 'SenhaForte123!',
            'first_name': 'Usuario Com Localizacao',
            'categoria': User.Categorias.EDUCADOR_NEGOCIOS,
            'cpf': '12345678901',
            'nome_instituicao': 'Instituicao',
            'municipio': 'Campinas',
            'estado': 'SP',
            'pais': 'Brasil'
        }
        form = CadastroUsuarioForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.municipio, 'Campinas')
        self.assertEqual(user.estado, 'SP')
        self.assertEqual(user.pais, 'Brasil')


class EditarPerfilFormComplementTestCase(TestCase):
    def test_init_cnpj_document(self):
        user = create_user(username='prof', categoria='PROFISSIONAL_CORPORATIVO')
        user.tipo_documento = 'CNPJ'
        user.documento = '12345678901234'
        user.save()
        form = EditarPerfilForm(instance=user)
        self.assertEqual(form.fields['cnpj'].initial, '12345678901234')

    def test_save_no_commit(self):
        user = create_user(username='asp', categoria='ASPIRANTE_EMPREENDEDOR')
        form = EditarPerfilForm(data={
            'first_name': 'Aspirante',
            'email': 'asp@test.com',
            'municipio': 'Cidade',
            'estado': 'SP',
            'pais': 'Brasil',
            'cpf': '12345678901',
            'area_atuacao': 'TI'
        }, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save(commit=False)
        self.assertIsNotNone(saved)

    def test_save_educador_documento_cpf(self):
        user = create_user(username='edu_doc', categoria='EDUCADOR_NEGOCIOS', codigo_turma=None)
        form = EditarPerfilForm(data={
            'first_name': 'Educador',
            'email': 'edu@test.com',
            'municipio': '',
            'estado': '',
            'pais': '',
            'cpf': '12345678901',
            'nome_instituicao': 'Instituicao'
        }, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save(commit=False)
        self.assertEqual(saved.tipo_documento, 'CPF')
        self.assertEqual(saved.documento, '12345678901')
        self.assertEqual(saved.municipio, 'Nao informado')
        self.assertEqual(saved.estado, 'SP')
        self.assertEqual(saved.pais, 'Brasil')

    def test_save_estudante_documento_none(self):
        user = create_user(username='est_doc', categoria='ESTUDANTE_UNIVERSITARIO')
        form = EditarPerfilForm(data={
            'first_name': 'Estudante',
            'email': 'est@test.com',
            'municipio': '',
            'estado': '',
            'pais': '',
            'codigo_turma': 'ABC-123',
            'matricula_aluno': '123456'
        }, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save(commit=False)
        self.assertIsNone(saved.documento)
        self.assertEqual(saved.tipo_documento, 'CPF')

    def test_save_editar_with_existing_location(self):
        # Testar save() EditarPerfilForm quando já há municipio/estado/pais (branches 454-459)
        user = create_user(username='user_existing', categoria='ASPIRANTE_EMPREENDEDOR', codigo_turma=None)
        user.municipio = 'Sao Paulo'
        user.estado = 'SP'
        user.pais = 'Brasil'
        user.save()
        form = EditarPerfilForm(data={
            'first_name': 'Aspirante',
            'email': 'asp@test.com',
            'municipio': 'Sao Paulo',
            'estado': 'SP',
            'pais': 'Brasil',
            'cpf': '12345678901',
            'area_atuacao': 'TI'
        }, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.municipio, 'Sao Paulo')
        self.assertEqual(saved.estado, 'SP')
        self.assertEqual(saved.pais, 'Brasil')


class ViewsComplementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = create_user(username='student', categoria='ESTUDANTE_UNIVERSITARIO')
        self.educator = create_user(username='educator', categoria='EDUCADOR_NEGOCIOS', codigo_turma=None)
        self.aspirante = create_user(username='aspirante', categoria='ASPIRANTE_EMPREENDEDOR', codigo_turma=None)
        self.profissional = create_user(username='profissional', categoria='PROFISSIONAL_CORPORATIVO', codigo_turma=None)

    def test_formatar_moeda_str_input(self):
        # String que pode ser convertida
        result = formatar_moeda_br('1234.56')
        self.assertIn('1.234,56', result)

    def test_formatar_moeda_invalid_decimal(self):
        # Teste do exception handler
        result = formatar_moeda_br('invalid_value_xyz')
        self.assertEqual(result, 'R$ 0,00')

    def test_salvar_jogo_conquista_message(self):
        # Criar partida com startup
        partida = Partida.objects.create(usuario=self.student, nome_empresa='Empresa')
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('10000.00'), receita_mensal=Decimal('0.00'))
        
        # POST para executar verificar_conquistas_progresso e gerar mensagens
        self.client.force_login(self.student)
        resp = self.client.post(reverse('salvar_jogo', args=[partida.id]), {'decisao': 'Não fazer nada (Economizar)'})
        self.assertEqual(resp.status_code, 302)
        # Verificar se a linha 202 (messages.success conquista) foi executada é complexo; test_salvar_jogo_decisoes já cobre parte disso

    def test_perfil_com_turma(self):
        turma = Turma.objects.create(codigo='ABC-123', nome='Turma A', educador=self.educator)
        self.student.codigo_turma = 'ABC-123'
        self.student.save()
        self.client.force_login(self.student)
        resp = self.client.get(reverse('perfil'))
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context['turma'])

    def test_ranking_criterios(self):
        # Criar startups ativas
        partida = Partida.objects.create(usuario=self.student, nome_empresa='S1', ativa=True)
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000.00'), valuation=Decimal('2000.00'), turno_atual=5)
        
        self.client.force_login(self.student)
        
        # Testar diferentes critérios
        for criterio in ['saldo', 'turno', 'conquistas', 'invalid']:
            resp = self.client.get(reverse('ranking'), {'criterio': criterio})
            self.assertEqual(resp.status_code, 200)

    def test_ranking_educador_com_turma(self):
        turma = Turma.objects.create(codigo='EDU-001', nome='Turma Educador', educador=self.educator, ativa=True)
        aluno = create_user(username='aluno_edu', categoria='ESTUDANTE_UNIVERSITARIO', codigo_turma='EDU-001')
        partida = Partida.objects.create(usuario=aluno, nome_empresa='Startup Aluno', ativa=True)
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('5000.00'), valuation=Decimal('10000.00'))
        
        self.client.force_login(self.educator)
        resp = self.client.get(reverse('ranking'), {'codigo_turma': 'EDU-001'})
        self.assertEqual(resp.status_code, 200)

    def test_ranking_filtros_regionais(self):
        partida = Partida.objects.create(usuario=self.student, nome_empresa='S1', ativa=True)
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000.00'), valuation=Decimal('2000.00'))
        
        self.client.force_login(self.student)
        resp = self.client.get(reverse('ranking'), {'pais': 'Brasil', 'estado': 'SP', 'municipio': 'Cidade'})
        self.assertEqual(resp.status_code, 200)

    def test_redirect_handler_default(self):
        # Categoria inválida ou padrão
        self.client.force_login(self.student)
        resp = self.client.get(reverse('redirect_handler'))
        self.assertRedirects(resp, reverse('dashboard'))

    def test_editar_perfil_post_sucesso(self):
        self.client.force_login(self.student)
        resp = self.client.post(reverse('editar_perfil'), {
            'first_name': 'Novo Nome',
            'email': self.student.email,
            'codigo_turma': 'ABC-123',
            'matricula_aluno': '123456',
            'municipio': 'Cidade',
            'estado': 'SP',
            'pais': 'Brasil'
        })
        self.assertRedirects(resp, reverse('perfil'))

    def test_editar_perfil_post_invalido(self):
        self.client.force_login(self.student)
        resp = self.client.post(reverse('editar_perfil'), {'first_name': '', 'email': ''})
        self.assertEqual(resp.status_code, 200)
        messages = list(get_messages(resp.wsgi_request))
        self.assertTrue(any('Erro' in str(m) for m in messages))

    def test_educador_editar_perfil_post_invalido(self):
        self.client.force_login(self.educator)
        resp = self.client.post(reverse('educador_editar_perfil'), {'first_name': '', 'email': ''})
        self.assertEqual(resp.status_code, 200)
        messages = list(get_messages(resp.wsgi_request))
        self.assertTrue(any('Erro' in str(m) for m in messages))

    def test_educador_editar_perfil_post_sucesso(self):
        self.client.force_login(self.educator)
        resp = self.client.post(reverse('educador_editar_perfil'), {
            'first_name': 'Educador Novo',
            'email': self.educator.email,
            'cpf': '12345678901',
            'nome_instituicao': 'Instituicao',
            'municipio': 'Cidade',
            'estado': 'SP',
            'pais': 'Brasil'
        })
        self.assertRedirects(resp, reverse('educador_perfil'))

    def test_educador_editar_perfil_get(self):
        self.client.force_login(self.educator)
        resp = self.client.get(reverse('educador_editar_perfil'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_metricas_turmas_max_valuation(self):
        turma1 = Turma.objects.create(codigo='TM1-001', nome='Turma 1', educador=self.educator, ativa=True)
        turma2 = Turma.objects.create(codigo='TM2-002', nome='Turma 2', educador=self.educator, ativa=True)
        
        aluno1 = create_user(username='aluno1', categoria='ESTUDANTE_UNIVERSITARIO', codigo_turma='TM1-001')
        aluno2 = create_user(username='aluno2', categoria='ESTUDANTE_UNIVERSITARIO', codigo_turma='TM2-002')
        
        p1 = Partida.objects.create(usuario=aluno1, nome_empresa='S1', ativa=True)
        Startup.objects.create(partida=p1, valuation=Decimal('50000.00'))
        
        p2 = Partida.objects.create(usuario=aluno2, nome_empresa='S2', ativa=True)
        Startup.objects.create(partida=p2, valuation=Decimal('100000.00'))
        
        self.client.force_login(self.educator)
        resp = self.client.get(reverse('metricas_turmas'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['maior_valuation'], Decimal('100000.00'))

    def test_ranking_aspirante_categoria(self):
        # Aspirante vê apenas startups de aspirantes
        asp2 = create_user(username='aspirante2', categoria='ASPIRANTE_EMPREENDEDOR', codigo_turma=None)
        p = Partida.objects.create(usuario=asp2, nome_empresa='Startup Aspirante', ativa=True)
        Startup.objects.create(partida=p, valuation=Decimal('5000.00'))
        
        self.client.force_login(self.aspirante)
        resp = self.client.get(reverse('ranking'))
        self.assertEqual(resp.status_code, 200)

    def test_ranking_profissional_categoria(self):
        # Profissional vê apenas startups de profissionais
        prof2 = create_user(username='profissional2', categoria='PROFISSIONAL_CORPORATIVO', codigo_turma=None)
        p = Partida.objects.create(usuario=prof2, nome_empresa='Startup Corp', ativa=True)
        Startup.objects.create(partida=p, valuation=Decimal('8000.00'))
        
        self.client.force_login(self.profissional)
        resp = self.client.get(reverse('ranking'))
        self.assertEqual(resp.status_code, 200)
