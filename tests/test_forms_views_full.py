"""
Cobertura total de forms.py e views.py
"""
from decimal import Decimal
from unittest.mock import patch

from django import forms
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.forms import CadastroUsuarioForm, EditarPerfilForm
from core.models import Partida, Startup, Turma, HistoricoDecisao
from core.views import formatar_moeda_br

User = get_user_model()


# Helpers

def base_user_data(**overrides):
    data = {
        'username': 'user_base',
        'email': 'user_base@test.com',
        'password1': 'SenhaForte123!',
        'password2': 'SenhaForte123!',
        'first_name': 'Usuario Teste',
        'categoria': 'ESTUDANTE_UNIVERSITARIO',
        'codigo_turma': 'ABC-123',
        'matricula_aluno': '123456',
    }
    data.update(overrides)
    return data


def create_user(username='user', categoria='ESTUDANTE_UNIVERSITARIO'):
    return User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='SenhaForte123!',
        categoria=categoria,
        municipio='Cidade',
        estado='SP',
        pais='Brasil'
    )


class CadastroUsuarioFormBranchesTestCase(TestCase):
    def test_username_too_long(self):
        data = base_user_data(username='a' * 151, email='long@test.com')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_username_too_short(self):
        data = base_user_data(username='ab', email='short@test.com')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_username_invalid_chars(self):
        data = base_user_data(username='inv#lid', email='chars@test.com')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_username_duplicate(self):
        create_user(username='dup')
        data = base_user_data(username='dup', email='dup2@test.com')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_email_invalid_format(self):
        data = base_user_data(email='invalid_email')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_email_duplicate(self):
        create_user(username='mail', categoria='ESTUDANTE_UNIVERSITARIO')
        data = base_user_data(email='mail@test.com', username='mail2')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_confirmation_missing(self):
        data = base_user_data(password2='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        data = base_user_data(password2='OutraSenha123!')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_strength_uppercase_missing(self):
        data = base_user_data(password1='senha1234', password2='senha1234')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_first_name_invalid_chars(self):
        data = base_user_data(first_name='123')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_municipio_too_long(self):
        data = base_user_data(municipio='a' * 101)
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_municipio_too_short(self):
        data = base_user_data(municipio='A')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_estado_invalid(self):
        data = base_user_data(estado='ZZ')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_pais_invalid(self):
        data = base_user_data(pais='XX')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_estudante_missing_codigo_turma(self):
        data = base_user_data(codigo_turma='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_estudante_missing_matricula(self):
        data = base_user_data(matricula_aluno='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_estudante_matricula_invalida(self):
        data = base_user_data(matricula_aluno='ABC')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_educador_missing_cpf_nome(self):
        data = base_user_data(categoria='EDUCADOR_NEGOCIOS', cpf='', nome_instituicao='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_educador_cpf_invalido(self):
        data = base_user_data(categoria='EDUCADOR_NEGOCIOS', cpf='123', nome_instituicao='Inst')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_aspirante_missing_campos(self):
        data = base_user_data(categoria='ASPIRANTE_EMPREENDEDOR', cpf='', area_atuacao='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_aspirante_area_muito_curta(self):
        data = base_user_data(categoria='ASPIRANTE_EMPREENDEDOR', cpf='12345678901', area_atuacao='A')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_aspirante_area_muito_longa(self):
        data = base_user_data(categoria='ASPIRANTE_EMPREENDEDOR', cpf='12345678901', area_atuacao='A'*101)
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_profissional_missing_campos(self):
        data = base_user_data(categoria='PROFISSIONAL_CORPORATIVO', cnpj='', nome_empresa='')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_profissional_cnpj_invalido(self):
        data = base_user_data(categoria='PROFISSIONAL_CORPORATIVO', cnpj='123', nome_empresa='Empresa')
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_profissional_nome_muito_longo(self):
        data = base_user_data(categoria='PROFISSIONAL_CORPORATIVO', cnpj='12345678901234', nome_empresa='E'*101)
        form = CadastroUsuarioForm(data=data)
        self.assertFalse(form.is_valid())

    def test_defaults_localizacao(self):
        data = base_user_data(municipio='', estado='', pais='', categoria='ASPIRANTE_EMPREENDEDOR', cpf='12345678901', area_atuacao='TI')
        form = CadastroUsuarioForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.pais, 'Brasil')
        self.assertEqual(user.estado, 'SP')
        self.assertEqual(user.municipio, 'Nao informado')

    def test_save_profissional_documento_cnpj(self):
        data = base_user_data(categoria='PROFISSIONAL_CORPORATIVO', cnpj='12345678901234', nome_empresa='Empresa')
        form = CadastroUsuarioForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.documento, '12345678901234')
        self.assertEqual(user.tipo_documento, 'CNPJ')


class EditarPerfilFormBranchesTestCase(TestCase):
    def test_codigo_turma_obrigatorio_para_estudante(self):
        user = create_user(username='aluno', categoria='ESTUDANTE_UNIVERSITARIO')
        form = EditarPerfilForm(data={'first_name': 'Aluno', 'email': 'a@test.com', 'municipio': '', 'estado': '', 'pais': ''}, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_turma', form.errors)

    def test_defaults_localizacao(self):
        user = create_user(username='asp', categoria='ASPIRANTE_EMPREENDEDOR')
        form = EditarPerfilForm(data={'first_name': 'Aspirante', 'email': 'asp@test.com', 'municipio': '', 'estado': '', 'pais': ''}, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.pais, 'Brasil')
        self.assertEqual(saved.estado, 'SP')
        self.assertEqual(saved.municipio, 'Nao informado')

    def test_save_documento_por_categoria(self):
        user = create_user(username='prof', categoria='PROFISSIONAL_CORPORATIVO')
        form = EditarPerfilForm(data={
            'first_name': 'Prof', 'email': 'prof@test.com', 'municipio': 'Cidade', 'estado': 'SP', 'pais': 'Brasil',
            'cnpj': '12345678901234'
        }, instance=user)
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.documento, '12345678901234')
        self.assertEqual(saved.tipo_documento, 'CNPJ')

    def test_init_cpf_cnpj_pre_popula(self):
        user = create_user(username='edu', categoria='EDUCADOR_NEGOCIOS')
        user.tipo_documento = 'CPF'
        user.documento = '12345678901'
        user.save()
        form = EditarPerfilForm(instance=user)
        self.assertEqual(form.fields['cpf'].initial, '12345678901')


class ViewsFullCoverageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = create_user(username='student', categoria='ESTUDANTE_UNIVERSITARIO')
        self.educator = create_user(username='educator', categoria='EDUCADOR_NEGOCIOS')

    def test_formatar_moeda_none(self):
        self.assertEqual(formatar_moeda_br(None), 'R$ 0,00')

    def test_formatar_moeda_exception(self):
        with patch('core.views.Decimal', side_effect=TypeError):
            self.assertEqual(formatar_moeda_br('bad'), 'R$ 0,00')

    def test_registro_get(self):
        resp = self.client.get(reverse('registro'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_registro_post_sucesso(self):
        data = base_user_data(username='novo_user', email='novo@test.com')
        resp = self.client.post(reverse('registro'), data)
        self.assertEqual(resp.status_code, 302)

    def test_salvar_jogo_partida_ativa_false(self):
        partida = Partida.objects.create(usuario=self.student, nome_empresa='Empresa X', ativa=False)
        self.client.force_login(self.student)
        resp = self.client.post(reverse('salvar_jogo', args=[partida.id]), {'decisao': 'Investir em Marketing Agressivo'})
        self.assertEqual(resp.status_code, 302)

    def test_salvar_jogo_sem_startup(self):
        partida = Partida.objects.create(usuario=self.student, nome_empresa='Sem Startup', ativa=True)
        self.client.force_login(self.student)
        resp = self.client.post(reverse('salvar_jogo', args=[partida.id]), {'decisao': 'Investir em Marketing Agressivo'})
        self.assertEqual(resp.status_code, 302)

    def _nova_partida_com_saldo(self, saldo):
        partida = Partida.objects.create(usuario=self.student, nome_empresa='Empresa Y')
        Startup.objects.create(partida=partida, saldo_caixa=Decimal(saldo), receita_mensal=Decimal('0.00'))
        return partida

    def test_salvar_jogo_saldo_insuficiente(self):
        partida = self._nova_partida_com_saldo('100.00')
        self.client.force_login(self.student)
        resp = self.client.post(reverse('salvar_jogo', args=[partida.id]), {'decisao': 'Contratar Engenheiro Sênior'})
        self.assertEqual(resp.status_code, 302)

    def test_salvar_jogo_decisoes(self):
        partida = self._nova_partida_com_saldo('10000.00')
        self.client.force_login(self.student)
        for decisao in ['Investir em Marketing Agressivo', 'Contratar Engenheiro Sênior', 'Não fazer nada (Economizar)']:
            resp = self.client.post(reverse('salvar_jogo', args=[partida.id]), {'decisao': decisao})
            self.assertEqual(resp.status_code, 302)

    def test_conquistas_bloqueio_educador(self):
        self.client.force_login(self.educator)
        resp = self.client.get(reverse('conquistas'))
        self.assertEqual(resp.status_code, 302)

    def test_historico_bloqueio_educador(self):
        self.client.force_login(self.educator)
        resp = self.client.get(reverse('historico'))
        self.assertEqual(resp.status_code, 302)

    def test_ranking_categorias(self):
        # Criar startup de estudante
        partida = Partida.objects.create(usuario=self.student, nome_empresa='S1')
        Startup.objects.create(partida=partida, saldo_caixa=Decimal('1000.00'), valuation=Decimal('2000.00'))
        self.client.force_login(self.student)
        resp = self.client.get(reverse('ranking'), {'criterio': 'saldo'})
        self.assertEqual(resp.status_code, 200)

    def test_redirect_handler_por_categoria(self):
        for cat, url_name in [
            (User.Categorias.ESTUDANTE_UNIVERSITARIO, 'dashboard'),
            (User.Categorias.ASPIRANTE_EMPREENDEDOR, 'dashboard'),
            (User.Categorias.EDUCADOR_NEGOCIOS, 'educador_dashboard'),
            (User.Categorias.PROFISSIONAL_CORPORATIVO, 'dashboard'),
        ]:
            user = create_user(username=f'user_{cat}', categoria=cat)
            self.client.force_login(user)
            resp = self.client.get(reverse('redirect_handler'))
            self.assertEqual(resp.status_code, 302)

    def test_editar_perfil_form_invalido(self):
        self.client.force_login(self.student)
        resp = self.client.post(reverse('editar_perfil'), {'first_name': '', 'email': ''})
        self.assertEqual(resp.status_code, 200)

    def test_educador_editar_perfil_invalido(self):
        self.client.force_login(self.educator)
        resp = self.client.post(reverse('educador_editar_perfil'), {'first_name': '', 'email': ''})
        self.assertEqual(resp.status_code, 200)

    def test_criar_turma_post_e_get(self):
        self.client.force_login(self.educator)
        resp = self.client.post(reverse('criar_turma'), {'nome_turma': 'T1', 'descricao_turma': 'Desc'})
        self.assertEqual(resp.status_code, 302)
        resp_get = self.client.get(reverse('criar_turma'))
        self.assertEqual(resp_get.status_code, 302)

    def test_gerar_codigo_turma_post_e_get(self):
        self.client.force_login(self.educator)
        resp = self.client.post(reverse('gerar_codigo_turma'))
        self.assertEqual(resp.status_code, 302)
        resp_get = self.client.get(reverse('gerar_codigo_turma'))
        self.assertEqual(resp_get.status_code, 302)
