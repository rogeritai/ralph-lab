import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline  # noqa: E402

PIVOT = ROOT / "pivot_receita.csv"


@pytest.fixture(scope="module")
def linhas():
    pipeline.main()
    with open(PIVOT, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_cabecalho_exato(linhas):
    assert linhas[0] == [
        "regiao", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"
    ]


def test_quatro_linhas_sete_colunas(linhas):
    dados = linhas[1:]
    assert [l[0] for l in dados] == ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]
    assert all(len(l) == 7 for l in dados)


def test_soma_total_pivot(linhas):
    total = sum(float(v) for l in linhas[1:] for v in l[1:])
    assert total == pytest.approx(931274.06, abs=0.50)


def test_formato_valores(linhas):
    for l in linhas[1:]:
        for v in l[1:]:
            inteiro, _, decimais = v.partition(".")
            assert inteiro.isdigit() and len(decimais) == 2


def test_sudeste_lider(linhas):
    totais = {l[0]: sum(float(v) for v in l[1:]) for l in linhas[1:]}
    lider = max(totais, key=totais.get)
    assert lider == "Sudeste"
    assert totais["Sudeste"] == pytest.approx(265077.49, abs=0.50)
