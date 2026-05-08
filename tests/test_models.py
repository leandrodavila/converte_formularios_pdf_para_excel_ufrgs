from src.models import FormData, ExtractionResult


def test_form_data_from_extracted_data():
    extracted = {
        "codigo_participante": "001",
        "data_coleta": "2026-05-08",
        "nome_completo": "João Silva"
    }

    form_data = FormData.from_extracted_data(
        data=extracted,
        filename="form001.pdf",
        quilombo="Comunidade Palmares"
    )

    assert form_data.quilombo == "Comunidade Palmares"
    assert form_data.arquivo == "form001.pdf"
    assert form_data.codigo_participante == "001"
    assert form_data.data_coleta == "2026-05-08"
    assert form_data.nome_completo == "João Silva"


def test_form_data_to_dict():
    form_data = FormData(
        quilombo="Test Quilombo",
        arquivo="test.pdf",
        codigo_participante="001",
        data_coleta="2026-05-08",
        nome_completo="Test Name",
        local_nascimento_criacao="",
        sexo_biologico="",
        genero="",
        idade="",
        data_nascimento="",
        cor_raca="",
        nome_mae="",
        cor_raca_mae="",
        local_nascimento_mae="",
        nome_pai="",
        cor_raca_pai="",
        local_nascimento_pai="",
        medicamentos="",
        troca_tratamento_6meses="",
        interrompeu_medicacao="",
        reacao_adversa="",
        ultima_pressao_arterial="",
        ultimo_exame_glicemia="",
        ultimo_exame_colesterol="",
        diagnosticos_proprios="",
        historico_familiar="",
        altura_cm="",
        peso_kg="",
        imc="",
        gordura_corporal_pct="",
        massa_muscular_pct="",
        gordura_visceral="",
        cintura_cm="",
        barriga_cm="",
        quadril_cm="",
        frequencia_cardiaca_bpm="",
        glicemia_mgdl="",
        temperatura_corporal="",
        pressao_arterial_pas="",
        pressao_arterial_pad="",
        horas_sem_alimentar=""
    )

    data_dict = form_data.to_dict()
    assert data_dict["quilombo"] == "Test Quilombo"
    assert data_dict["arquivo"] == "test.pdf"
    assert isinstance(data_dict, dict)


def test_extraction_result_success():
    form_data = FormData(
        quilombo="Test", arquivo="test.pdf", codigo_participante="001",
        data_coleta="", nome_completo="", local_nascimento_criacao="",
        sexo_biologico="", genero="", idade="", data_nascimento="",
        cor_raca="", nome_mae="", cor_raca_mae="", local_nascimento_mae="",
        nome_pai="", cor_raca_pai="", local_nascimento_pai="", medicamentos="",
        troca_tratamento_6meses="", interrompeu_medicacao="", reacao_adversa="",
        ultima_pressao_arterial="", ultimo_exame_glicemia="", ultimo_exame_colesterol="",
        diagnosticos_proprios="", historico_familiar="", altura_cm="", peso_kg="",
        imc="", gordura_corporal_pct="", massa_muscular_pct="", gordura_visceral="",
        cintura_cm="", barriga_cm="", quadril_cm="", frequencia_cardiaca_bpm="",
        glicemia_mgdl="", temperatura_corporal="", pressao_arterial_pas="",
        pressao_arterial_pad="", horas_sem_alimentar=""
    )

    result = ExtractionResult(
        filename="test.pdf",
        success=True,
        data=form_data,
        error=None,
        attempts=1,
        duration_seconds=2.5
    )

    assert result.success is True
    assert result.data is not None
    assert result.error is None


def test_extraction_result_failure():
    result = ExtractionResult(
        filename="test.pdf",
        success=False,
        data=None,
        error="API timeout",
        attempts=3,
        duration_seconds=10.0
    )

    assert result.success is False
    assert result.data is None
    assert result.error == "API timeout"
