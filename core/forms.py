from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CadastroUsuarioForm(UserCreationForm):
    # Declaramos os campos explicitamente para forçar a renderização
    email = forms.EmailField(label="E-mail", required=True)
    tipo_documento = forms.ChoiceField(label="Tipo de Documento", choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')])
    documento = forms.CharField(label="CPF/CNPJ", max_length=18)
    categoria = forms.ChoiceField(label="Categoria", choices=User.Categorias.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'tipo_documento', 'documento', 'categoria')

    def clean_documento(self):
        doc = self.cleaned_data.get('documento')
        return "".join(filter(str.isdigit, doc)) if doc else doc