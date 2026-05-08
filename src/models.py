from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class FormData:
    """Extracted form data from a single PDF"""
    quilombo: str
    arquivo: str
    codigo_participante: str
    data_coleta: str
    nome_completo: str
    local_nascimento_criacao: str
    sexo_biologico: str
    genero: str
    idade: str
    data_nascimento: str
    cor_raca: str
    nome_mae: str
    cor_raca_mae: str
    local_nascimento_mae: str
    nome_pai: str
    cor_raca_pai: str
    local_nascimento_pai: str
    medicamentos: str
    troca_tratamento_6meses: str
    interrompeu_medicacao: str
    reacao_adversa: str
    ultima_pressao_arterial: str
    ultimo_exame_glicemia: str
    ultimo_exame_colesterol: str
    diagnosticos_proprios: str
    historico_familiar: str
    altura_cm: str
    peso_kg: str
    imc: str
    gordura_corporal_pct: str
    massa_muscular_pct: str
    gordura_visceral: str
    cintura_cm: str
    barriga_cm: str
    quadril_cm: str
    frequencia_cardiaca_bpm: str
    glicemia_mgdl: str
    temperatura_corporal: str
    pressao_arterial_pas: str
    pressao_arterial_pad: str
    horas_sem_alimentar: str

    @classmethod
    def from_extracted_data(
        cls,
        data: dict[str, str],
        filename: str,
        quilombo: str
    ) -> "FormData":
        """
        Create FormData from extracted JSON + metadata.

        Args:
            data: Extracted field values from API
            filename: PDF filename
            quilombo: Quilombo name (from CLI or folder)

        Returns:
            FormData instance with all fields populated
        """
        return cls(
            quilombo=quilombo,
            arquivo=filename,
            codigo_participante=data.get("codigo_participante", ""),
            data_coleta=data.get("data_coleta", ""),
            nome_completo=data.get("nome_completo", ""),
            local_nascimento_criacao=data.get("local_nascimento_criacao", ""),
            sexo_biologico=data.get("sexo_biologico", ""),
            genero=data.get("genero", ""),
            idade=data.get("idade", ""),
            data_nascimento=data.get("data_nascimento", ""),
            cor_raca=data.get("cor_raca", ""),
            nome_mae=data.get("nome_mae", ""),
            cor_raca_mae=data.get("cor_raca_mae", ""),
            local_nascimento_mae=data.get("local_nascimento_mae", ""),
            nome_pai=data.get("nome_pai", ""),
            cor_raca_pai=data.get("cor_raca_pai", ""),
            local_nascimento_pai=data.get("local_nascimento_pai", ""),
            medicamentos=data.get("medicamentos", ""),
            troca_tratamento_6meses=data.get("troca_tratamento_6meses", ""),
            interrompeu_medicacao=data.get("interrompeu_medicacao", ""),
            reacao_adversa=data.get("reacao_adversa", ""),
            ultima_pressao_arterial=data.get("ultima_pressao_arterial", ""),
            ultimo_exame_glicemia=data.get("ultimo_exame_glicemia", ""),
            ultimo_exame_colesterol=data.get("ultimo_exame_colesterol", ""),
            diagnosticos_proprios=data.get("diagnosticos_proprios", ""),
            historico_familiar=data.get("historico_familiar", ""),
            altura_cm=data.get("altura_cm", ""),
            peso_kg=data.get("peso_kg", ""),
            imc=data.get("imc", ""),
            gordura_corporal_pct=data.get("gordura_corporal_pct", ""),
            massa_muscular_pct=data.get("massa_muscular_pct", ""),
            gordura_visceral=data.get("gordura_visceral", ""),
            cintura_cm=data.get("cintura_cm", ""),
            barriga_cm=data.get("barriga_cm", ""),
            quadril_cm=data.get("quadril_cm", ""),
            frequencia_cardiaca_bpm=data.get("frequencia_cardiaca_bpm", ""),
            glicemia_mgdl=data.get("glicemia_mgdl", ""),
            temperatura_corporal=data.get("temperatura_corporal", ""),
            pressao_arterial_pas=data.get("pressao_arterial_pas", ""),
            pressao_arterial_pad=data.get("pressao_arterial_pad", ""),
            horas_sem_alimentar=data.get("horas_sem_alimentar", "")
        )

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for Excel export"""
        return asdict(self)


@dataclass
class ExtractionResult:
    """Result of processing a single PDF"""
    filename: str
    success: bool
    data: Optional[FormData]
    error: Optional[str]
    attempts: int
    duration_seconds: float

    def __str__(self) -> str:
        """Human-readable status string"""
        if self.success:
            return f"✅ {self.filename} ({self.duration_seconds:.2f}s)"
        else:
            return f"❌ {self.filename}: {self.error} ({self.attempts} attempts)"
