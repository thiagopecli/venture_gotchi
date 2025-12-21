from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, TipoUsuario

class RegistroEstudanteForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    
    class Meta:
        model = PerfilUsuario
        fields = ['cpf', 'nome_completo', 'telefone']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem')
        
        return cleaned_data

class RegistroProfessorForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    
    class Meta:
        model = PerfilUsuario
        fields = ['cpf', 'nome_completo', 'telefone']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem')
        
        return cleaned_data

class RegistroStartupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    
    class Meta:
        model = PerfilUsuario
        fields = ['cnpj', 'razao_social', 'telefone']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem')
        
        return cleaned_data

class RegistroEmpresaForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailEmail()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirmar Senha')
    
    class Meta:
        model = PerfilUsuario
        fields = ['cnpj', 'razao_social', 'telefone']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('As senhas não coincidem')
        
        return cleaned_data