from memori.oral.checklist import coverage_report, detect_gaps

SEGMENTOS = [
    {
        "inicio_ms": 0,
        "fin_ms": 3000,
        "texto": "I was born in Bahia Blanca. My mother sewed for the neighbors and my father worked on the railway.",
    },
    {
        "inicio_ms": 3000,
        "fin_ms": 6000,
        "texto": "I remember we played in the neighborhood until it got dark.",
    },
]


def test_detect_gaps_marks_missing_categories():
    gaps = detect_gaps(SEGMENTOS)
    categorias = {g["categoria"] for g in gaps}
    assert "migration" in categorias
    assert "childhood" not in categorias
    assert "family" not in categorias
    assert "work" not in categorias
    assert "memories" not in categorias


def test_coverage_report_percentages():
    report = coverage_report(SEGMENTOS)
    assert report["total"] == 5
    assert report["porcentaje"] > 0
    assert report["porcentaje"] < 100
    assert report["huecos"]
