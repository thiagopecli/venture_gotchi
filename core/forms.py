from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CadastroUsuarioForm(UserCreationForm):
    # Declaramos os campos explicitamente para forçar a renderização
    first_name = forms.CharField(label="Nome Completo", required=True) # Campo para o nome real
    email = forms.EmailField(label="E-mail", required=True)
    tipo_documento = forms.ChoiceField(label="Tipo de Documento", choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')])
    documento = forms.CharField(label="CPF/CNPJ", max_length=18)
    categoria = forms.ChoiceField(label="Categoria", choices=User.Categorias.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'email', 'tipo_documento', 'documento', 'categoria', 'municipio', 'estado', 'pais')

    def clean_documento(self):
        doc = self.cleaned_data.get('documento')
        tipo = self.cleaned_data.get('tipo_documento')
        if doc:
            doc_clean = "".join(filter(str.isdigit, doc))
            if tipo == 'CPF' and len(doc_clean) != 11:
                raise forms.ValidationError('CPF deve ter exatamente 11 dígitos.')
            elif tipo == 'CNPJ' and len(doc_clean) != 14:
                raise forms.ValidationError('CNPJ deve ter exatamente 14 dígitos.')
            return doc_clean
        return doc