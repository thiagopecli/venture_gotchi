from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario
from .models import (
    Conquista,
    ConquistaDesbloqueada,
    Evento,
    EventoPartida,
    Fundador,
    HistoricoDecisao,
    Partida,
    Startup,
)


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_empresa", "usuario", "data_inicio")
    list_filter = ("data_inicio",)
    search_fields = ("nome_empresa", "usuario__username")


@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "partida",
        "saldo_caixa",
        "receita_mensal",
        "valuation",
        "funcionarios",
        "turno_atual",
    )
    search_fields = ("partida__nome_empresa",)


@admin.register(HistoricoDecisao)
class HistoricoDecisaoAdmin(admin.ModelAdmin):
    list_display = ("id", "partida", "turno", "data_decisao")
    list_filter = ("turno", "data_decisao")
    search_fields = ("partida__nome_empresa", "decisao_tomada")


@admin.register(Fundador)
class FundadorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "partida", "experiencia", "anos_experiencia")
    list_filter = ("experiencia",)
    search_fields = ("nome", "partida__nome_empresa")


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "categoria", "chance_base", "ativo")
    list_filter = ("categoria", "ativo")
    search_fields = ("titulo", "descricao")


@admin.register(EventoPartida)
class EventoPartidaAdmin(admin.ModelAdmin):
    list_display = ("id", "partida", "evento", "turno", "resolvido", "criado_em")
    list_filter = ("turno", "resolvido")
    search_fields = ("partida__nome_empresa", "evento__titulo")


@admin.register(Conquista)
class ConquistaAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "tipo", "valor_objetivo", "pontos", "ativo")
    list_filter = ("tipo", "ativo")
    search_fields = ("titulo", "descricao")


@admin.register(ConquistaDesbloqueada)
class ConquistaDesbloqueadaAdmin(admin.ModelAdmin):
    list_display = ("id", "partida", "conquista", "turno", "desbloqueada_em")
    list_filter = ("turno",)
    search_fields = ("partida__nome_empresa", "conquista__titulo")

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_tipo_usuario')
    list_select_related = ('perfil',)
    
    def get_tipo_usuario(self, instance):
        if hasattr(instance, 'perfil'):
            return instance.perfil.get_tipo_usuario_display()
        return '-'
    get_tipo_usuario.short_description = 'Tipo de Usuário'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'cpf', 'cnpj', 'nome_completo', 'created_at')
    list_filter = ('tipo_usuario', 'created_at')
    search_fields = ('user__username', 'nome_completo', 'cpf', 'cnpj', 'razao_social')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'tipo_usuario')
        }),
        ('Dados Pessoais (CPF)', {
            'fields': ('cpf', 'nome_completo'),
            'classes': ('collapse',),
        }),
        ('Dados Empresariais (CNPJ)', {
            'fields': ('cnpj', 'razao_social'),
            'classes': ('collapse',),
        }),
        ('Contato', {
            'fields': ('telefone',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)