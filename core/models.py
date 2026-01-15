from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.conf import settings

class User(AbstractUser):
    class Categorias(models.TextChoices):
        # Categorias para CPF
        ALUNO = "ALUNO", "Aluno (CPF)"
        PROFESSOR = "PROFESSOR", "Professor (CPF)"
        STARTUP_PF = "STARTUP_PF", "Startup (CPF - Pré-formalizada)"
        
        # Categorias para CNPJ
        STARTUP_PJ = "STARTUP_PJ", "Startup (CNPJ)"
        EMPRESA = "EMPRESA", "Empresa (CNPJ)"
        INSTITUICAO = "INSTITUICAO", "Instituição de Ensino (CNPJ)"

    tipo_documento = models.CharField(
        max_length=4, 
        choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')],
        default='CPF'
    )
    documento = models.CharField(max_length=18, unique=True, help_text="CPF ou CNPJ")
    categoria = models.CharField(max_length=20, choices=Categorias.choices)
    municipio = models.CharField(max_length=100, verbose_name="Município", blank=True, null=True)
    estado = models.CharField(max_length=100, verbose_name="Estado", blank=True, null=True)
    pais = models.CharField(max_length=100, verbose_name="País", default="Brasil", blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.categoria}"

class Partida(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Sempre use esta referência
        on_delete=models.CASCADE,
        related_name='partidas',
        db_index=True
    )
    nome_empresa = models.CharField(max_length=100)
    data_inicio = models.DateTimeField(auto_now_add=True, db_index=True)
    ativa = models.BooleanField(default=True, help_text='Indica se a partida está em andamento')
    data_fim = models.DateTimeField(null=True, blank=True, help_text='Data de conclusão da partida')
    
    class Meta:
        ordering = ['-data_inicio']
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
        indexes = [
            models.Index(fields=['usuario', '-data_inicio'], name='idx_usuario_data'),
            models.Index(fields=['ativa', 'usuario'], name='idx_ativa_usuario'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=models.F('data_inicio')),
                name='data_fim_maior_que_inicio'
            ),
        ]
    
    def __str__(self):
        return f"Partida de {self.nome_empresa}"


class Startup(models.Model):
    """Modelo para as métricas da empresa (Startup)"""
    partida = models.OneToOneField(
        Partida, 
        on_delete=models.CASCADE, 
        related_name='startup',
        primary_key=True  # Garante relação 1:1 no nível do BD
    )
    saldo_caixa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('00.00'))
    turno_atual = models.PositiveIntegerField(default=1)
    nome = models.CharField(max_length=100, default="Minha Startup")
    receita_mensal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valuation = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('00.00'))
    funcionarios = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(turno_atual__gte=1),
                name='turno_minimo_1'
            ),
            models.CheckConstraint(
                condition=models.Q(funcionarios__gte=0),
                name='funcionarios_nao_negativo'
            ),
            models.CheckConstraint(
                condition=models.Q(receita_mensal__gte=0),
                name='receita_nao_negativa'
            ),
            models.CheckConstraint(
                condition=models.Q(valuation__gte=0),
                name='valuation_nao_negativo'
            ),
        ]
    
    def __str__(self):
        return self.nome


class HistoricoDecisao(models.Model):
    """Modelo para registrar o histórico de decisões"""
    partida = models.ForeignKey(
        Partida, 
        on_delete=models.CASCADE, 
        related_name='decisoes',
        db_index=True
    )
    decisao_tomada = models.TextField()
    turno = models.PositiveIntegerField()
    data_decisao = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['turno']
        verbose_name = 'Histórico de Decisão'
        verbose_name_plural = 'Históricos de Decisões'
        indexes = [
            models.Index(fields=['partida', 'turno'], name='idx_partida_turno'),
            models.Index(fields=['partida', '-data_decisao'], name='idx_partida_data_decisao_desc'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(turno__gte=1),
                name='historico_turno_minimo_1'
            ),
        ]

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

    partida = models.OneToOneField(
        Partida, 
        on_delete=models.CASCADE, 
        related_name='fundador',
        primary_key=True
    )
    nome = models.CharField(max_length=100)
    idade = models.PositiveSmallIntegerField(default=25, validators=[MinValueValidator(16)])
    experiencia = models.CharField(max_length=20, choices=Experiencia.choices, default=Experiencia.TECNOLOGIA)
    anos_experiencia = models.PositiveSmallIntegerField(default=0)
    habilidades = models.TextField(blank=True)
    motivacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Fundador'
        verbose_name_plural = 'Fundadores'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(idade__gte=16) & models.Q(idade__lte=120),
                name='idade_valida'
            ),
            models.CheckConstraint(
                condition=models.Q(anos_experiencia__lte=models.F('idade') - 16),
                name='anos_experiencia_coerente'
            ),
        ]

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

    titulo = models.CharField(max_length=150, unique=True, db_index=True)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=Categoria.choices, db_index=True)
    chance_base = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default=Decimal('0.1'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Probabilidade entre 0 e 1.',
    )
    impacto_saldo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impacto_receita = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impacto_valuation = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impacto_funcionarios = models.IntegerField(default=0)
    turno_minimo = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        indexes = [
            models.Index(fields=['categoria', 'ativo'], name='idx_categoria_ativo'),
            models.Index(fields=['turno_minimo', 'ativo'], name='idx_turno_ativo'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(chance_base__gte=0) & models.Q(chance_base__lte=1),
                name='chance_entre_0_e_1'
            ),
            models.CheckConstraint(
                condition=models.Q(turno_minimo__gte=1),
                name='evento_turno_minimo_1'
            ),
        ]

    def __str__(self):
        return self.titulo

class EventoPartida(models.Model):
    """Ocorrência concreta de um evento em uma partida."""

    partida = models.ForeignKey(
        Partida, 
        on_delete=models.CASCADE, 
        related_name='eventos',
        db_index=True
    )
    evento = models.ForeignKey(
        Evento, 
        on_delete=models.PROTECT, 
        related_name='ocorrencias',
        db_index=True
    )
    turno = models.PositiveIntegerField()
    resolvido = models.BooleanField(default=False, db_index=True)
    resultado = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['turno']
        verbose_name = 'Evento da Partida'
        verbose_name_plural = 'Eventos da Partida'
        indexes = [
            models.Index(fields=['partida', 'turno'], name='idx_evento_partida_turno'),
            models.Index(fields=['partida', 'resolvido'], name='idx_partida_resolvido'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['partida', 'evento', 'turno'], 
                name='unique_evento_partida_turno'
            ),
            models.CheckConstraint(
                condition=models.Q(turno__gte=1),
                name='evento_partida_turno_minimo_1'
            ),
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

    titulo = models.CharField(max_length=150, unique=True, db_index=True)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=Tipo.choices, db_index=True)
    valor_objetivo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pontos = models.PositiveIntegerField(default=10)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['titulo']
        verbose_name = 'Conquista'
        verbose_name_plural = 'Conquistas'
        indexes = [
            models.Index(fields=['tipo', 'ativo'], name='idx_conquista_tipo_ativo'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor_objetivo__gte=0),
                name='valor_objetivo_nao_negativo'
            ),
            models.CheckConstraint(
                condition=models.Q(pontos__gte=0),
                name='pontos_nao_negativo'
            ),
        ]

    def __str__(self):
        return self.titulo

class ConquistaDesbloqueada(models.Model):
    """Registro de conquistas liberadas em uma partida."""

    partida = models.ForeignKey(
        Partida, 
        on_delete=models.CASCADE, 
        related_name='conquistas',
        db_index=True
    )
    conquista = models.ForeignKey(
        Conquista, 
        on_delete=models.PROTECT, 
        related_name='desbloqueios',
        db_index=True
    )
    turno = models.PositiveIntegerField(default=1)
    desbloqueada_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-desbloqueada_em']
        verbose_name = 'Conquista Desbloqueada'
        verbose_name_plural = 'Conquistas Desbloqueadas'
        indexes = [
            models.Index(fields=['partida', 'turno'], name='idx_conquista_partida_turno'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['partida', 'conquista'], 
                name='unique_conquista_por_partida'
            ),
            models.CheckConstraint(
                condition=models.Q(turno__gte=1),
                name='conquista_turno_minimo_1'
            ),
        ]

    def __str__(self):
        return f"{self.conquista.titulo} - {self.partida.nome_empresa}"