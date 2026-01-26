from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
import re
from .models import User, Turma

class CadastroUsuarioForm(UserCreationForm):
    username = forms.CharField(
        label="Nome de usuário",
        max_length=150,
        help_text="Obrigatório. Até 150 caracteres."
    )
    # Declaramos os campos explicitamente para forçar a renderização
    first_name = forms.CharField(label="Nome Completo", required=True) # Campo para o nome real
    email = forms.EmailField(label="E-mail", required=True)
    tipo_documento = forms.ChoiceField(label="Tipo de Documento", choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')], required=False)
    documento = forms.CharField(label="CPF/CNPJ", max_length=18, required=False)
    categoria = forms.ChoiceField(label="Categoria", choices=User.Categorias.choices)
    codigo_turma = forms.CharField(label="Código de Turma", required=False, max_length=100, validators=[RegexValidator(r'^[A-Z]{3}-[0-9]{3}$', 'Código de Turma deve estar no formato AAA-999.')])
    matricula_aluno = forms.CharField(label="Matrícula do Aluno", required=False, max_length=10, validators=[RegexValidator(r'^\d{1,10}$', 'Matrícula deve ter até 10 dígitos numéricos.')])
    cpf = forms.CharField(
        label="CPF", 
        required=False, 
        max_length=11,
        validators=[RegexValidator(r'^\d{11}$', 'CPF deve ter exatamente 11 dígitos.')],
        widget=forms.TextInput(attrs={
            'maxlength': '11',
            'inputmode': 'numeric',
            'pattern': '[0-9]{11}',
            'placeholder': '11 dígitos'
        })
    )
    nome_instituicao = forms.CharField(
        label="Nome da Instituição", 
        required=False, 
        max_length=100,
        help_text="Obrigatório para educadores. Máximo: 100 caracteres."
    )
    area_atuacao = forms.CharField(
        label="Área de Atuação", 
        required=False, 
        max_length=100,
        help_text="Obrigatório para aspirantes a empreendedor. Máximo: 100 caracteres.",
        widget=forms.TextInput(attrs={
            'maxlength': '100',
            'placeholder': 'Ex: Tecnologia, Saúde, Educação'
        })
    )
    cnpj = forms.CharField(
        label="CNPJ",
        required=False,
        max_length=14,
        validators=[RegexValidator(r'^\d{14}$', 'CNPJ deve ter exatamente 14 dígitos.')],
        widget=forms.TextInput(attrs={
            'maxlength': '14',
            'inputmode': 'numeric',
            'pattern': '[0-9]{14}',
            'placeholder': '14 dígitos'
        })
    )
    nome_empresa = forms.CharField(
        label="Nome da Empresa",
        required=False,
        max_length=100,
        help_text="Obrigatório para profissionais corporativos. Máximo: 100 caracteres."
    )
    municipio = forms.CharField(
        label="Município",
        required=False,
        max_length=100,
        help_text="Opcional. Caso omita, será usado um valor padrão."
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=User.Estados.choices,
        help_text="Opcional. Caso omita, será usado 'SP'."
    )
    pais = forms.ChoiceField(
        label="País",
        required=False,
        choices=User.Paises.choices,
        initial='Brasil',
        help_text="Opcional. Caso omita, será usado 'Brasil'."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'email', 'categoria', 'codigo_turma', 'matricula_aluno', 'cpf', 'nome_instituicao', 'area_atuacao', 'cnpj', 'nome_empresa', 'municipio', 'estado', 'pais')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Desabilitar validadores padrão de senha do Django
        # para usar apenas nossos validadores customizados
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []

    def clean_username(self):
        """Valida o nome de usuário com mensagens específicas"""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError("Nome de usuário é obrigatório.")
        
        if len(username) > 150:
            raise forms.ValidationError(f"Nome de usuário não pode ter mais de 150 caracteres (você digitou {len(username)}).")
        
        if len(username) < 3:
            raise forms.ValidationError("Nome de usuário deve ter no mínimo 3 caracteres.")
        
        # Verificar caracteres válidos
        if not re.match(r'^[a-zA-Z0-9._@+-]+$', username):
            raise forms.ValidationError("Nome de usuário pode conter apenas letras, números, e os caracteres: . @ + -")
        
        # Verificar se já existe
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"O nome de usuário '{username}' já está em uso. Escolha outro.")
        
        return username

    def clean_email(self):
        """Valida o e-mail com mensagens específicas"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("E-mail é obrigatório.")
        
        # Validação de formato
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError("Formato de e-mail inválido. Use um e-mail válido (exemplo: usuario@dominio.com).")
        
        # Verificar se já existe
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Este e-mail ('{email}') já está registrado. Use outro e-mail ou recupere sua senha.")
        
        return email

    def clean_password2(self):
        """Valida a senha com critérios específicos"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password2:
            raise forms.ValidationError("Confirmação de senha é obrigatória.")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem. Verifique e tente novamente.")
        
        # Validações de força da senha - adicionar no campo password1
        if password1:
            errors = []
            
            if len(password1) < 8:
                errors.append(f"Senha muito curta (tem {len(password1)} caracteres, mínimo é 8)")
            
            if not re.search(r'[A-Z]', password1):
                errors.append("Senha deve conter pelo menos uma letra MAIÚSCULA")
            
            if not re.search(r'[a-z]', password1):
                errors.append("Senha deve conter pelo menos uma letra minúscula")
            
            if not re.search(r'[0-9]', password1):
                errors.append("Senha deve conter pelo menos um número")
            
            if password1.lower() == self.cleaned_data.get('username', '').lower():
                errors.append("Senha não pode ser igual ao nome de usuário")
            
            if errors:
                # Adicionar erros no campo password1 em vez de password2
                for error in errors:
                    self.add_error('password1', error)
        
        return password2

    def clean_first_name(self):
        """Valida o nome completo"""
        first_name = self.cleaned_data.get('first_name')
        
        if not first_name:
            raise forms.ValidationError("Nome completo é obrigatório.")
        
        if len(first_name) > 150:
            raise forms.ValidationError(f"Nome não pode ter mais de 150 caracteres (você digitou {len(first_name)}).")
        
        if len(first_name) < 3:
            raise forms.ValidationError("Nome deve ter no mínimo 3 caracteres.")
        
        if not re.match(r'^[a-zA-Záéíóúàâêôãõç\s\.-]+$', first_name):
            raise forms.ValidationError("Nome pode conter apenas letras, espaços, pontos e hífens.")
        
        return first_name

    def clean_municipio(self):
        """Valida o município"""
        municipio = self.cleaned_data.get('municipio')
        if not municipio:
            return municipio
        if len(municipio) > 100:
            raise forms.ValidationError(f"Nome do município não pode ter mais de 100 caracteres (você digitou {len(municipio)}).")
        if len(municipio) < 2:
            raise forms.ValidationError("Nome do município deve ter no mínimo 2 caracteres.")
        return municipio

    def clean_estado(self):
        """Valida o estado"""
        estado = self.cleaned_data.get('estado')
        if not estado:
            return estado
        if estado not in dict(User.Estados.choices).keys():
            raise forms.ValidationError("Selecione um estado válido.")
        return estado

    def clean_pais(self):
        """Valida o país"""
        pais = self.cleaned_data.get('pais')
        if not pais:
            return pais
        if pais not in dict(User.Paises.choices).keys():
            raise forms.ValidationError("Selecione um país válido.")
        return pais

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')

        # Valores padrão para localização quando omitidos
        if not cleaned_data.get('municipio'):
            cleaned_data['municipio'] = 'Nao informado'
        if not cleaned_data.get('estado'):
            cleaned_data['estado'] = 'SP'
        if not cleaned_data.get('pais'):
            cleaned_data['pais'] = 'Brasil'
        
        if categoria == User.Categorias.ESTUDANTE_UNIVERSITARIO:
            errors = {}
            codigo_turma = cleaned_data.get('codigo_turma')
            if not codigo_turma:
                errors['codigo_turma'] = 'Código de turma é obrigatório para estudantes universitários.'
            else:
                # Normaliza para maiúsculas
                codigo_turma = codigo_turma.upper()
                cleaned_data['codigo_turma'] = codigo_turma
                
                # Valida se a turma existe e está ativa no banco de dados
                turma = Turma.objects.filter(codigo__iexact=codigo_turma, ativa=True).first()
                if not turma:
                    errors['codigo_turma'] = f"A turma com código '{codigo_turma}' não existe ou está inativa no banco de dados. Verifique o código e tente novamente."
            
            matricula = cleaned_data.get('matricula_aluno')
            if not matricula:
                errors['matricula_aluno'] = 'Matrícula do aluno é obrigatória para estudantes universitários.'
            elif not re.match(r'^\d{1,10}$', matricula):
                errors['matricula_aluno'] = f"Matrícula inválida. Deve conter apenas números (máximo 10 dígitos). Você digitou: '{matricula}'"
            
            if errors:
                raise forms.ValidationError(errors)
            
            # Para estudante, documento deve ser None
            cleaned_data['documento'] = None
            cleaned_data['tipo_documento'] = 'CPF'
        
        elif categoria == User.Categorias.EDUCADOR_NEGOCIOS:
            errors = {}
            cpf = cleaned_data.get('cpf')
            if not cpf:
                errors['cpf'] = 'CPF é obrigatório para educadores de negócios.'
            elif not re.match(r'^\d{11}$', cpf):
                errors['cpf'] = f"CPF inválido. Deve conter exatamente 11 dígitos numéricos. Você digitou: '{cpf}'"
            
            nome_inst = cleaned_data.get('nome_instituicao')
            if not nome_inst:
                errors['nome_instituicao'] = 'Nome da instituição é obrigatório para educadores de negócios.'
            elif len(nome_inst) > 100:
                errors['nome_instituicao'] = f"Nome da instituição muito longo ({len(nome_inst)} caracteres, máximo é 100)."
            
            if errors:
                raise forms.ValidationError(errors)
            
            # Definir tipo_documento e documento
            cleaned_data['tipo_documento'] = 'CPF'
            cleaned_data['documento'] = cpf
        
        elif categoria == User.Categorias.ASPIRANTE_EMPREENDEDOR:
            errors = {}
            cpf = cleaned_data.get('cpf')
            if not cpf:
                errors['cpf'] = 'CPF é obrigatório para aspirantes a empreendedor.'
            elif not re.match(r'^\d{11}$', cpf):
                errors['cpf'] = f"CPF inválido. Deve conter exatamente 11 dígitos numéricos. Você digitou: '{cpf}'"
            
            area = cleaned_data.get('area_atuacao')
            if not area or not area.strip():
                errors['area_atuacao'] = 'Área de atuação é obrigatória para aspirantes a empreendedor. Por favor, informe sua área de atuação.'
            elif len(area) > 100:
                errors['area_atuacao'] = f"Área de atuação muito longa ({len(area)} caracteres, máximo é 100)."
            elif len(area.strip()) < 2:
                errors['area_atuacao'] = 'Área de atuação deve ter no mínimo 2 caracteres.'
            
            if errors:
                raise forms.ValidationError(errors)
            
            # Definir tipo_documento e documento
            cleaned_data['tipo_documento'] = 'CPF'
            cleaned_data['documento'] = cpf
        
        elif categoria == User.Categorias.PROFISSIONAL_CORPORATIVO:
            errors = {}
            cnpj = cleaned_data.get('cnpj')
            if not cnpj:
                errors['cnpj'] = 'CNPJ é obrigatório para profissionais corporativos.'
            elif not re.match(r'^\d{14}$', cnpj):
                errors['cnpj'] = f"CNPJ inválido. Deve conter exatamente 14 dígitos numéricos. Você digitou: '{cnpj}'"
            
            nome_emp = cleaned_data.get('nome_empresa')
            if not nome_emp:
                errors['nome_empresa'] = 'Nome da empresa é obrigatório para profissionais corporativos.'
            elif len(nome_emp) > 100:
                errors['nome_empresa'] = f"Nome da empresa muito longo ({len(nome_emp)} caracteres, máximo é 100)."
            
            if errors:
                raise forms.ValidationError(errors)
            
            # Para profissional, definir tipo_documento como CNPJ e documento como cnpj
            cleaned_data['tipo_documento'] = 'CNPJ'
            cleaned_data['documento'] = cnpj
        
        return cleaned_data
    
    def save(self, commit=True):
        """
        Override do save para mapear cpf/cnpj para documento
        """
        user = super().save(commit=False)
        
        # Garantir que tipo_documento e documento sejam definidos corretamente
        categoria = self.cleaned_data.get('categoria')
        
        if categoria == User.Categorias.EDUCADOR_NEGOCIOS:
            user.tipo_documento = 'CPF'
            user.documento = self.cleaned_data.get('cpf')
        elif categoria == User.Categorias.ASPIRANTE_EMPREENDEDOR:
            user.tipo_documento = 'CPF'
            user.documento = self.cleaned_data.get('cpf')
        elif categoria == User.Categorias.PROFISSIONAL_CORPORATIVO:
            user.tipo_documento = 'CNPJ'
            user.documento = self.cleaned_data.get('cnpj')
        elif categoria == User.Categorias.ESTUDANTE_UNIVERSITARIO:
            user.documento = None
            user.tipo_documento = 'CPF'

        # Garantir defaults de localização ao salvar
        if not user.municipio:
            user.municipio = 'Nao informado'
        if not user.estado:
            user.estado = 'SP'
        if not user.pais:
            user.pais = 'Brasil'
        
        if commit:
            user.save()
        return user

    
class EditarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome Completo", required=True)
    email = forms.EmailField(label="E-mail", required=True)
    municipio = forms.CharField(label="Município", required=False, max_length=100)
    estado = forms.ChoiceField(label="Estado", required=False, choices=User.Estados.choices)
    pais = forms.ChoiceField(label="País", required=False, choices=User.Paises.choices)
    codigo_turma = forms.CharField(label="Código de Turma", required=False, max_length=100, validators=[RegexValidator(r'^[A-Z]{3}-[0-9]{3}$', 'Formato AAA-999.')])
    matricula_aluno = forms.CharField(label="Matrícula", required=False, max_length=10)
    cpf = forms.CharField(
        label="CPF", 
        required=False, 
        max_length=11,
        widget=forms.TextInput(attrs={
            'maxlength': '11',
            'inputmode': 'numeric',
            'pattern': '[0-9]{11}',
            'placeholder': '11 dígitos'
        })
    )
    cnpj = forms.CharField(
        label="CNPJ",
        required=False,
        max_length=14,
        widget=forms.TextInput(attrs={
            'maxlength': '14',
            'inputmode': 'numeric',
            'pattern': '[0-9]{14}',
            'placeholder': '14 dígitos'
        })
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'email', 'municipio', 'estado', 'pais', 
            'codigo_turma', 'matricula_aluno', 'cpf', 'nome_instituicao', 
            'area_atuacao', 'cnpj', 'nome_empresa'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo_turma'].widget.attrs.update({'class': 'estudante-field'})
        self.fields['matricula_aluno'].widget.attrs.update({'class': 'estudante-field'})
        self.fields['cpf'].widget.attrs.update({'class': 'educador-field aspirante-field'})
        self.fields['nome_instituicao'].widget.attrs.update({'class': 'educador-field'})
        self.fields['area_atuacao'].widget.attrs.update({'class': 'aspirante-field'})
        self.fields['cnpj'].widget.attrs.update({'class': 'profissional-field'})
        self.fields['nome_empresa'].widget.attrs.update({'class': 'profissional-field'})
        
        # Preencher cpf e cnpj a partir do campo documento da instância
        if self.instance.pk:
            if self.instance.tipo_documento == 'CPF':
                self.fields['cpf'].initial = self.instance.documento
            elif self.instance.tipo_documento == 'CNPJ':
                self.fields['cnpj'].initial = self.instance.documento

    def clean(self):
        cleaned_data = super().clean()
        categoria = self.instance.categoria

        # Defaults para localização quando não informados
        if not cleaned_data.get('municipio'):
            cleaned_data['municipio'] = 'Nao informado'
        if not cleaned_data.get('estado'):
            cleaned_data['estado'] = 'SP'
        if not cleaned_data.get('pais'):
            cleaned_data['pais'] = 'Brasil'

        if categoria == 'ESTUDANTE_UNIVERSITARIO' and not cleaned_data.get('codigo_turma'):
            self.add_error('codigo_turma', 'Campo obrigatório para estudantes.')
        return cleaned_data
    
    def save(self, commit=True):
        """
        Override do save para mapear cpf/cnpj para documento
        """
        user = super().save(commit=False)
        categoria = user.categoria
        
        # Mapear cpf/cnpj para documento baseado na categoria
        if categoria == 'EDUCADOR_NEGOCIOS':
            user.tipo_documento = 'CPF'
            user.documento = self.cleaned_data.get('cpf')
        elif categoria == 'ASPIRANTE_EMPREENDEDOR':
            user.tipo_documento = 'CPF'
            user.documento = self.cleaned_data.get('cpf')
        elif categoria == 'PROFISSIONAL_CORPORATIVO':
            user.tipo_documento = 'CNPJ'
            user.documento = self.cleaned_data.get('cnpj')
        elif categoria == 'ESTUDANTE_UNIVERSITARIO':
            user.documento = None
            user.tipo_documento = 'CPF'

        # Persistir defaults de localização se não vieram do form
        if not user.municipio:
            user.municipio = 'Nao informado'
        if not user.estado:
            user.estado = 'SP'
        if not user.pais:
            user.pais = 'Brasil'
        
        if commit:
            user.save()
        return user
