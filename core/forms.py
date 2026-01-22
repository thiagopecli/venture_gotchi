from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User

class CadastroUsuarioForm(UserCreationForm):
    # Declaramos os campos explicitamente para forçar a renderização
    first_name = forms.CharField(label="Nome Completo", required=True) # Campo para o nome real
    email = forms.EmailField(label="E-mail", required=True)
    tipo_documento = forms.ChoiceField(label="Tipo de Documento", choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')], required=False)
    documento = forms.CharField(label="CPF/CNPJ", max_length=18, required=False)
    categoria = forms.ChoiceField(label="Categoria", choices=User.Categorias.choices)
    codigo_turma = forms.CharField(label="Código de Turma", required=False, max_length=100, validators=[RegexValidator(r'^[A-Z]{3}-[0-9]{3}$', 'Código de Turma deve estar no formato AAA-999.')])
    matricula_aluno = forms.CharField(label="Matrícula do Aluno", required=False, max_length=10, validators=[RegexValidator(r'^\d{1,10}$', 'Matrícula deve ter até 10 dígitos numéricos.')])
    cpf = forms.CharField(label="CPF", required=False, max_length=18, validators=[RegexValidator(r'^\d{11}$', 'CPF deve ter exatamente 11 dígitos.')])
    nome_instituicao = forms.CharField(label="Nome da Instituição", required=False, max_length=100)
    area_atuacao = forms.CharField(label="Área de Atuação", required=False, max_length=100)
    cnpj = forms.CharField(label="CNPJ", required=False, max_length=18, validators=[RegexValidator(r'^\d{14}$', 'CNPJ deve ter exatamente 14 dígitos.')])
    nome_empresa = forms.CharField(label="Nome da Empresa", required=False, max_length=100)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'email', 'categoria', 'codigo_turma', 'matricula_aluno', 'cpf', 'nome_instituicao', 'area_atuacao', 'cnpj', 'nome_empresa', 'municipio', 'estado', 'pais')

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        
        if categoria == User.Categorias.ESTUDANTE_UNIVERSITARIO:
            if not cleaned_data.get('codigo_turma'):
                raise forms.ValidationError({'codigo_turma': 'Este campo é obrigatório para Estudante Universitário.'})
            if not cleaned_data.get('matricula_aluno'):
                raise forms.ValidationError({'matricula_aluno': 'Este campo é obrigatório para Estudante Universitário.'})
            # Para estudante, documento deve ser None
            cleaned_data['documento'] = None
            cleaned_data['tipo_documento'] = 'CPF'
        
        elif categoria == User.Categorias.EDUCADOR_NEGOCIOS:
            if not cleaned_data.get('cpf'):
                raise forms.ValidationError({'cpf': 'Este campo é obrigatório para Educador de Negócios.'})
            if not cleaned_data.get('nome_instituicao'):
                raise forms.ValidationError({'nome_instituicao': 'Este campo é obrigatório para Educador de Negócios.'})
            # Definir tipo_documento e documento
            cleaned_data['tipo_documento'] = 'CPF'
            cleaned_data['documento'] = cleaned_data.get('cpf')
        
        elif categoria == User.Categorias.ASPIRANTE_EMPREENDEDOR:
            if not cleaned_data.get('cpf'):
                raise forms.ValidationError({'cpf': 'Este campo é obrigatório para Aspirante a Empreendedor.'})
            if not cleaned_data.get('area_atuacao'):
                raise forms.ValidationError({'area_atuacao': 'Este campo é obrigatório para Aspirante a Empreendedor.'})
            # Definir tipo_documento e documento
            cleaned_data['tipo_documento'] = 'CPF'
            cleaned_data['documento'] = cleaned_data.get('cpf')
        
        elif categoria == User.Categorias.PROFISSIONAL_CORPORATIVO:
            if not cleaned_data.get('cnpj'):
                raise forms.ValidationError({'cnpj': 'Este campo é obrigatório para Profissional Corporativo.'})
            if not cleaned_data.get('nome_empresa'):
                raise forms.ValidationError({'nome_empresa': 'Este campo é obrigatório para Profissional Corporativo.'})
            # Para profissional, definir tipo_documento como CNPJ e documento como cnpj
            cleaned_data['tipo_documento'] = 'CNPJ'
            cleaned_data['documento'] = cleaned_data.get('cnpj')
        
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email