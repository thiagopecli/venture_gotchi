from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator


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

class Fundador(models.Model):
    """Perfil do fundador vinculado a uma partida."""
    class Experiencia(models.TextChoices):
        TECNOLOGIA = 'tecnologia', 'Tecnologia'
        NEGOCIOS = 'negocios', 'Negócios'
        DESIGN = 'design', 'Design'
        PRODUTO = 'produto', 'Produto'
        OPERACOES = 'operacoes', 'Operações'

    partida = models.OneToOneField(Partida, on_delete=models.CASCADE, related_name='fundador')
    nome = models.CharField(max_length=100)
    idade = models.PositiveSmallIntegerField(default=25, validators=[MinValueValidator(16)])
    experiencia = models.CharField(max_length=20, choices=Experiencia.choices, default=Experiencia.TECNOLOGIA)
    anos_experiencia = models.PositiveSmallIntegerField(default=0)
    habilidades = models.TextField(blank=True)
    motivacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Fundador'
        verbose_name_plural = 'Fundadores'

    def __str__(self):
        return f"{self.nome} ({self.get_experiencia_display()})"

class Evento(models.Model):
    """Eventos potenciais que podem impactar a startup."""

    class Categoria(models.TextChoices):
        MERCADO = 'mercado', 'Mercado'
        PRODUTO = 'produto', 'Produto'
        EQUIPE = 'equipe', 'Equipe'
        INVESTIMENTO = 'investimento', 'Investimento'
        RISCO = 'risco', 'Risco'

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    chance_base = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default=0.1,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Probabilidade entre 0 e 1.',
    )
    impacto_saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impacto_receita = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impacto_valuation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impacto_funcionarios = models.IntegerField(default=0)
    turno_minimo = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.titulo

class EventoPartida(models.Model):
    """Ocorrência concreta de um evento em uma partida."""

    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='eventos')
    evento = models.ForeignKey(Evento, on_delete=models.PROTECT, related_name='ocorrencias')
    turno = models.PositiveIntegerField()
    resolvido = models.BooleanField(default=False)
    resultado = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['turno']
        verbose_name = 'Evento da Partida'
        verbose_name_plural = 'Eventos da Partida'
        constraints = [
            models.UniqueConstraint(fields=['partida', 'evento', 'turno'], name='unique_evento_partida_turno'),
        ]

    def __str__(self):
        return f"{self.evento.titulo} (T{self.turno})"

class Conquista(models.Model):
    """Catálogo de conquistas disponíveis no jogo."""
    class Tipo(models.TextChoices):
        PROGRESSO = 'progresso', 'Progresso'
        FINANCEIRO = 'financeiro', 'Financeiro'
        OPERACIONAL = 'operacional', 'Operacional'
        SOCIAL = 'social', 'Social'

    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    valor_objetivo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pontos = models.PositiveIntegerField(default=10)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Conquista'
        verbose_name_plural = 'Conquistas'

    def __str__(self):
        return self.titulo

class ConquistaDesbloqueada(models.Model):
    """Registro de conquistas liberadas em uma partida."""

    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='conquistas')
    conquista = models.ForeignKey(Conquista, on_delete=models.PROTECT, related_name='desbloqueios')
    turno = models.PositiveIntegerField(default=1)
    desbloqueada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-desbloqueada_em']
        verbose_name = 'Conquista Desbloqueada'
        verbose_name_plural = 'Conquistas Desbloqueadas'
        constraints = [
            models.UniqueConstraint(fields=['partida', 'conquista'], name='unique_conquista_por_partida'),
        ]

    def __str__(self):
        return f"{self.conquista.titulo} - {self.partida.nome_empresa}"
    
class TipoUsuario(models.TextChoices):
    ESTUDANTE = 'ESTUDANTE', 'Estudante'
    PROFESSOR = 'PROFESSOR', 'Professor'
    STARTUP = 'STARTUP', 'Startup'
    EMPRESA = 'EMPRESA', 'Empresa'

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices)
    
    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')]
    )
    
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        unique=True,
        validators=[RegexValidator(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')]
    )
    
    nome_completo = models.CharField(max_length=255)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        permissions = [
            ('visualizar_dashboard_estudante', 'Pode visualizar dashboard de estudante'),
            ('visualizar_dashboard_professor', 'Pode visualizar dashboard de professor'),
            ('visualizar_dashboard_startup', 'Pode visualizar dashboard de startup'),
            ('visualizar_dashboard_empresa', 'Pode visualizar dashboard de empresa'),
            ('gerenciar_usuarios', 'Pode gerenciar usuários'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"
    
    def save(self, *args, **kwargs):
        if self.tipo_usuario in [TipoUsuario.ESTUDANTE, TipoUsuario.PROFESSOR]:
            self.cnpj = None
        else:
            self.cpf = None
        super().save(*args, **kwargs)