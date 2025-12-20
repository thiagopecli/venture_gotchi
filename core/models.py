from django.db import models
from django.contrib.auth.models import User

class Partida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas')
    nome_empresa = models.CharField(max_length=100)
    data_inicio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome_empresa} - {self.usuario.username}"

class Startup(models.Model):
    partida = models.OneToOneField(Partida, on_delete=models.CASCADE, related_name='startup')
    saldo_caixa = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    turno_atual = models.IntegerField(default=1)

class HistoricoDecisao(models.Model):
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='decisoes')
    turno = models.IntegerField()
    decisao_tomada = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)