"""Models read-only do domínio Programas."""

from django.db import models

from apps.programas.enums import CategoriaPrograma


class TipoPrograma(models.Model):
    """Subtipos de programa por categoria (PAP/PAEE)."""

    codigo_tipo_programa = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaPrograma.choices,
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = "programas"
        db_table = "tipo_programa"
        managed = False
        verbose_name = "tipo de programa"
        verbose_name_plural = "tipos de programa"

    def __str__(self) -> str:
        return f"{self.nome} ({self.codigo_tipo_programa})"


class ComponenteCurricularPrograma(models.Model):
    """Componentes curriculares que caracterizam uma categoria de programa."""

    codigo_componente_curricular = models.BigIntegerField(unique=True)
    nome_componente_curricular = models.CharField(max_length=200)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaPrograma.choices,
    )
    vigente = models.BooleanField()

    class Meta:
        app_label = "programas"
        db_table = "componente_curricular_programa"
        managed = False
        verbose_name = "componente curricular de programa"
        verbose_name_plural = "componentes curriculares de programa"

    def __str__(self) -> str:
        return (
            f"{self.nome_componente_curricular}"
            f" ({self.codigo_componente_curricular})"
            f" — {self.categoria}"
        )


class TurmaPrograma(models.Model):
    """Turmas de programa."""

    codigo_turma = models.BigIntegerField(unique=True)
    nome_turma = models.CharField(max_length=200)
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20)
    ano_letivo = models.SmallIntegerField()
    tipo_turno = models.SmallIntegerField(null=True, blank=True)
    descricao_turno = models.CharField(max_length=100, blank=True, default="")
    descricao_grade = models.CharField(max_length=200, null=True, blank=True)
    situacao = models.CharField(max_length=1)
    codigo_tipo_programa = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaPrograma.choices,
    )
    criado_em = models.DateTimeField()
    atualizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "programas"
        db_table = "turma_programa"
        managed = False
        verbose_name = "turma de programa"
        verbose_name_plural = "turmas de programa"

    def __str__(self) -> str:
        return f"{self.nome_turma} ({self.codigo_turma}) — {self.ano_letivo}"


class TurmaProgramaComponenteCurricular(models.Model):
    """Componentes curriculares que uma turma de programa oferece."""

    codigo_turma = models.BigIntegerField()
    codigo_componente_curricular = models.BigIntegerField()
    nome_componente_curricular = models.CharField(max_length=200)
    criado_em = models.DateTimeField()

    class Meta:
        app_label = "programas"
        db_table = "turma_programa_componente_curricular"
        managed = False
        verbose_name = "componente curricular da turma"
        verbose_name_plural = "componentes curriculares das turmas"

    def __str__(self) -> str:
        return (
            f"Turma {self.codigo_turma}"
            f" — {self.nome_componente_curricular}"
            f" ({self.codigo_componente_curricular})"
        )


class MatriculaTurmaPrograma(models.Model):
    """Matrículas de alunos em turmas de programa, por componente."""

    codigo_aluno = models.BigIntegerField()
    codigo_turma = models.BigIntegerField()
    codigo_componente_curricular = models.BigIntegerField()
    nome_componente_curricular = models.CharField(max_length=200)
    codigo_situacao_matricula = models.SmallIntegerField()
    descricao_situacao_matricula = models.CharField(max_length=50)
    data_matricula = models.DateField()
    data_situacao = models.DateField(null=True, blank=True)
    ano_letivo = models.SmallIntegerField()
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaPrograma.choices,
    )
    criado_em = models.DateTimeField()
    atualizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "programas"
        db_table = "matricula_turma_programa"
        managed = False
        verbose_name = "matrícula em turma de programa"
        verbose_name_plural = "matrículas em turmas de programa"

    def __str__(self) -> str:
        return (
            f"Aluno {self.codigo_aluno}"
            f" — turma {self.codigo_turma}"
            f" / CC {self.codigo_componente_curricular}"
        )


class MatriculaTurmaProgramaHistorico(models.Model):
    """Matrículas históricas de alunos em turmas de programa."""

    codigo_aluno = models.BigIntegerField()
    codigo_turma = models.BigIntegerField()
    codigo_componente_curricular = models.BigIntegerField()
    nome_componente_curricular = models.CharField(max_length=200)
    codigo_situacao_matricula = models.SmallIntegerField()
    descricao_situacao_matricula = models.CharField(max_length=50)
    data_matricula = models.DateField(null=True, blank=True)
    data_situacao = models.DateField(null=True, blank=True)
    ano_letivo = models.SmallIntegerField()
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20)
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaPrograma.choices,
    )
    criado_em = models.DateTimeField()
    atualizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "programas"
        db_table = "matricula_turma_programa_historico"
        managed = False
        verbose_name = "matrícula histórica em turma de programa"
        verbose_name_plural = "matrículas históricas em turmas de programa"

    def __str__(self) -> str:
        return (
            f"Aluno {self.codigo_aluno}"
            f" — turma {self.codigo_turma}"
            f" / CC {self.codigo_componente_curricular}"
            f" (histórico)"
        )


class AlunoPapAnoLetivo(models.Model):
    """Alunos PAP por ano letivo, pré-agregados (carga live)."""

    # Materializada e filtrada pelo MS-ETL; este serviço apenas lê.
    codigo_aluno = models.BigIntegerField()
    codigo_turma = models.BigIntegerField()
    codigo_componente_curricular = models.BigIntegerField()
    ano_letivo = models.SmallIntegerField()
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20)

    class Meta:
        app_label = "programas"
        db_table = "aluno_pap_ano_letivo"
        managed = False
        verbose_name = "aluno PAP por ano letivo"
        verbose_name_plural = "alunos PAP por ano letivo"

    def __str__(self) -> str:
        return (
            f"Aluno {self.codigo_aluno}"
            f" — turma {self.codigo_turma}"
            f" / CC {self.codigo_componente_curricular}"
            f" ({self.ano_letivo})"
        )


class AlunoPapAnoLetivoHistorico(models.Model):
    """Alunos PAP por ano letivo, pré-agregados (carga histórica)."""

    # Materializada e filtrada pelo MS-ETL; este serviço apenas lê.
    codigo_aluno = models.BigIntegerField()
    codigo_turma = models.BigIntegerField()
    codigo_componente_curricular = models.BigIntegerField()
    ano_letivo = models.SmallIntegerField()
    codigo_ue = models.CharField(max_length=20)
    codigo_dre = models.CharField(max_length=20)

    class Meta:
        app_label = "programas"
        db_table = "aluno_pap_ano_letivo_historico"
        managed = False
        verbose_name = "aluno PAP por ano letivo (histórico)"
        verbose_name_plural = "alunos PAP por ano letivo (histórico)"

    def __str__(self) -> str:
        return (
            f"Aluno {self.codigo_aluno}"
            f" — turma {self.codigo_turma}"
            f" / CC {self.codigo_componente_curricular}"
            f" ({self.ano_letivo}, histórico)"
        )
