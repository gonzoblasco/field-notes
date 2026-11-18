from memori.oral.checklist import coverage_report, detect_gaps

SEGMENTOS = [
    {"inicio_ms": 0, "fin_ms": 3000, "texto": "Nací en Bahía Blanca, mi mamá cosía y mi papá trabajaba en el ferrocarril."},
    {"inicio_ms": 3000, "fin_ms": 6000, "texto": "Recuerdo que en el barrio jugábamos hasta que oscurecía."},
]


def test_detect_gaps_marks_missing_categories():
    gaps = detect_gaps(SEGMENTOS)
    categorias = {g["categoria"] for g in gaps}
    assert "migración" in categorias
    assert "niñez" not in categorias
    assert "familia" not in categorias
    assert "trabajo" not in categorias


def test_coverage_report_percentages():
    report = coverage_report(SEGMENTOS)
    assert report["total"] == 5
    assert report["porcentaje"] > 0
    assert report["porcentaje"] < 100
    assert report["huecos"]
