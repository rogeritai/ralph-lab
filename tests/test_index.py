import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline  # noqa: E402

INDEX = ROOT / "index.html"


@pytest.fixture(scope="module")
def pagina():
    pipeline.main()
    return INDEX.read_text(encoding="utf-8")


def _paragrafos(pagina):
    return [re.sub(r"<[^>]+>", "", p).strip()
            for p in re.findall(r"<p[^>]*>(.*?)</p>", pagina, re.S)]


def test_meta_charset(pagina):
    assert '<meta charset="utf-8">' in pagina


def test_canvas_e_chartjs(pagina):
    assert "<canvas" in pagina
    assert "chart.js" in pagina.lower()


def test_paragrafo_conclusao_300_caracteres(pagina):
    assert any(len(p) >= 300 for p in _paragrafos(pagina))


def test_conclusao_cita_valores(pagina):
    conclusao = max(_paragrafos(pagina), key=len)
    assert "R$ 931.274,06" in conclusao
    assert "Sudeste" in conclusao and "R$ 265.077,49" in conclusao
    assert "R$ 8.120,00" in conclusao
    assert "id_loja=999" in conclusao
    assert "108" in conclusao


def test_dados_do_grafico(pagina):
    for regiao in ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]:
        assert f'"label": "{regiao}"' in pagina
    for mes in ["2026-01", "2026-06"]:
        assert f'"{mes}"' in pagina
