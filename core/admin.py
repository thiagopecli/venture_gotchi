from django.contrib import admin

from .models import (
    Conquista,
    ConquistaDesbloqueada,
    Evento,
    EventoPartida,
    Fundador,
    HistoricoDecisao,
    Partida,
    Startup,
    Turma,
)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "educador", "ativa", "data_criacao")
    list_filter = ("ativa", "data_criacao")
    search_fields = ("codigo", "nome", "educador__username")
    list_select_related = ("educador",)
    readonly_fields = ("data_criacao",)


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("id", "nome_empresa", "usuario", "data_inicio")
    list_filter = ("data_inicio",)
    search_fields = ("nome_empresa", "usuario__username")
    list_select_related = ("usuario",)


@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = (
        "partida",
        "nome",
        "saldo_caixa",
        "receita_mensal",
        "valuation",
        "funcionarios",
        "turno_atual",
    )
    search_fields = ("partida__nome_empresa", "nome")
    list_select_related = ("partida",)


@admin.register(HistoricoDecisao)
class HistoricoDecisaoAdmin(admin.ModelAdmin):
    list_display = ("id", "partida", "turno", "data_decisao")
    list_filter = ("turno", "data_decisao")
    search_fields = ("partida__nome_empresa", "decisao_tomada")
    list_select_related = ("partida",)


@admin.register(Fundador)
class FundadorAdmin(admin.ModelAdmin):
    list_display = ("partida", "nome", "experiencia", "anos_experiencia", "idade")
    list_filter = ("experiencia",)
    search_fields = ("nome", "partida__nome_empresa")
    list_select_related = ("partida",)


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
    list_select_related = ("partida", "evento")


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
    list_select_related = ("partida", "conquista")
