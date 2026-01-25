from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from decimal import Decimal
from django.conf import settings
import random
import string

class Turma(models.Model):
    """Modelo para turmas criadas por educadores"""
    codigo = models.CharField(
        max_length=7, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z]{3}-[0-9]{3}$', 'Código deve estar no formato AAA-999.')],
        verbose_name='Código da Turma'
    )
    nome = models.CharField(max_length=100, verbose_name='Nome da Turma')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    educador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='turmas_criadas',
        limit_choices_to={'categoria': 'EDUCADOR_NEGOCIOS'}
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True, verbose_name='Turma Ativa')
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    @staticmethod
    def gerar_codigo_unico():
        """Gera um código único no formato AAA-999"""
        while True:
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            numeros = ''.join(random.choices(string.digits, k=3))
            codigo = f"{letras}-{numeros}"
            
            if not Turma.objects.filter(codigo=codigo).exists():
                return codigo

class User(AbstractUser):
    class Categorias(models.TextChoices):
        ESTUDANTE_UNIVERSITARIO = "ESTUDANTE_UNIVERSITARIO", "Estudante Universitário"
        ASPIRANTE_EMPREENDEDOR = "ASPIRANTE_EMPREENDEDOR", "Aspirante a Empreendedor"
        EDUCADOR_NEGOCIOS = "EDUCADOR_NEGOCIOS", "Educador de Negócios"
        PROFISSIONAL_CORPORATIVO = "PROFISSIONAL_CORPORATIVO", "Profissional Corporativo"
    
    class Estados(models.TextChoices):
        AC = 'AC', 'Acre'
        AL = 'AL', 'Alagoas'
        AP = 'AP', 'Amapá'
        AM = 'AM', 'Amazonas'
        BA = 'BA', 'Bahia'
        CE = 'CE', 'Ceará'
        DF = 'DF', 'Distrito Federal'
        ES = 'ES', 'Espírito Santo'
        GO = 'GO', 'Goiás'
        MA = 'MA', 'Maranhão'
        MT = 'MT', 'Mato Grosso'
        MS = 'MS', 'Mato Grosso do Sul'
        MG = 'MG', 'Minas Gerais'
        PA = 'PA', 'Pará'
        PB = 'PB', 'Paraíba'
        PR = 'PR', 'Paraná'
        PE = 'PE', 'Pernambuco'
        PI = 'PI', 'Piauí'
        RJ = 'RJ', 'Rio de Janeiro'
        RN = 'RN', 'Rio Grande do Norte'
        RS = 'RS', 'Rio Grande do Sul'
        RO = 'RO', 'Rondônia'
        RR = 'RR', 'Roraima'
        SC = 'SC', 'Santa Catarina'
        SP = 'SP', 'São Paulo'
        SE = 'SE', 'Sergipe'
        TO = 'TO', 'Tocantins'
    
    class Paises(models.TextChoices):
        BRASIL = 'Brasil', 'Brasil'

    tipo_documento = models.CharField(
        max_length=4, 
        choices=[('CPF', 'CPF'), ('CNPJ', 'CNPJ')],
        default='CPF'
    )
    documento = models.CharField(max_length=18, unique=True, blank=True, null=True, help_text="CPF ou CNPJ")
    categoria = models.CharField(max_length=30, choices=Categorias.choices)
    municipio = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(max_length=2, verbose_name="Estado", choices=Estados.choices)
    pais = models.CharField(max_length=100, verbose_name="País", choices=Paises.choices, default='Brasil')
    codigo_turma = models.CharField(max_length=100, verbose_name="Código de Turma", blank=True, null=True, validators=[RegexValidator(r'^[A-Z]{3}-[0-9]{3}$', 'Código de Turma deve estar no formato AAA-999.')])
    matricula_aluno = models.CharField(max_length=10, verbose_name="Matrícula do Aluno", blank=True, null=True, validators=[RegexValidator(r'^\d{1,10}$', 'Matrícula deve ter até 10 dígitos numéricos.')])
    nome_instituicao = models.CharField(max_length=100, verbose_name="Nome da Instituição", blank=True, null=True)
    area_atuacao = models.CharField(max_length=100, verbose_name="Área de Atuação", blank=True, null=True)
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ", blank=True, null=True, validators=[RegexValidator(r'^\d{14}$', 'CNPJ deve ter exatamente 14 dígitos.')])
    nome_empresa = models.CharField(max_length=100, verbose_name="Nome da Empresa", blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.categoria}"
    
    # Métodos de Permissões
    def is_estudante(self):
        """Verifica se é Estudante Universitário"""
        return self.categoria == self.Categorias.ESTUDANTE_UNIVERSITARIO
    
    def is_aspirante(self):
        """Verifica se é Aspirante a Empreendedor"""
        return self.categoria == self.Categorias.ASPIRANTE_EMPREENDEDOR
    
    def is_educador(self):
        """Verifica se é Educador de Negócios"""
        return self.categoria == self.Categorias.EDUCADOR_NEGOCIOS
    
    def is_profissional(self):
        """Verifica se é Profissional Corporativo"""
        return self.categoria == self.Categorias.PROFISSIONAL_CORPORATIVO
    
    # Permissões específicas
    def pode_salvar_carregar_partida(self):
        """Estudantes, Aspirantes e Profissionais Corporativos podem salvar/carregar partidas"""
        return self.is_estudante() or self.is_aspirante() or self.is_profissional()
    
    def pode_visualizar_propria_partida(self):
        """Estudantes, Aspirantes e Profissionais Corporativos podem visualizar suas próprias partidas"""
        return self.is_estudante() or self.is_aspirante() or self.is_profissional()
    
    def pode_acessar_relatorios_agregados(self):
        """Apenas Educadores podem acessar relatórios agregados"""
        return self.is_educador()
    
    def pode_acessar_ranking(self):
        """Estudantes, Aspirantes, Profissionais e Educadores podem acessar ranking"""
        return self.is_estudante() or self.is_aspirante() or self.is_profissional() or self.is_educador()
    
    def pode_desbloquear_conquistas(self):
        """Estudantes, Aspirantes e Profissionais Corporativos podem desbloquear conquistas"""
        return self.is_estudante() or self.is_aspirante() or self.is_profissional()
    
    def pode_visualizar_conquistas(self):
        """Todos podem visualizar conquistas"""
        return True

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
        ordering = ['-valuation', 'nome']
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