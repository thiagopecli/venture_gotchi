from django.db import models
from django.contrib.auth.models import User


class Partida(models.Model):
    """Modelo para a sessão de jogo (Partida)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_empresa = models.CharField(max_length=100)
    data_inicio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_inicio']
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
    
    def __str__(self):
        return f"Partida de {self.nome_empresa}"


class Startup(models.Model):
    """Modelo para as métricas da empresa (Startup)"""
    partida = models.OneToOneField(Partida, on_delete=models.CASCADE, related_name='startup')
    saldo_caixa = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    turno_atual = models.IntegerField(default=1)
    nome = models.CharField(max_length=100, default="Minha Startup")
    receita_mensal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valuation = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    funcionarios = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'
    
    def __str__(self):
        return self.nome


class HistoricoDecisao(models.Model):
    """Modelo para registrar o histórico de decisões"""
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='decisoes')
    decisao_tomada = models.TextField()
    turno = models.IntegerField()
    data_decisao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['turno']
        verbose_name = 'Histórico de Decisão'
        verbose_name_plural = 'Históricos de Decisões'

    def __str__(self):
        return f"Decisão no turno {self.turno}"