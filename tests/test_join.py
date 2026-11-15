import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline  # noqa: E402

VENDAS_LOJAS = ROOT / "vendas_lojas.csv"


@pytest.fixture(scope="module")
def linhas():
    pipeline.main()
    with open(VENDAS_LOJAS, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_vendas_lojas_tem_420_linhas(linhas):
    assert len(linhas) == 420


def test_soma_receita_vendas_lojas(linhas):
    total = sum(float(l["receita_brl"]) for l in linhas)
    assert total == pytest.approx(931274.06, abs=0.50)


def test_colunas_e_orfas_fora(linhas):
    assert "receita_brl" in linhas[0]
    assert "regiao" in linhas[0]
    ids = {l["id_venda"] for l in linhas}
    assert ids.isdisjoint({"V00421", "V00422", "V00423"})
    assert all(l["id_loja"] != "999" for l in linhas)
