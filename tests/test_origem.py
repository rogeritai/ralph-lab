import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline  # noqa: E402


def contar_linhas_dados(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def test_vendas_tem_423_linhas():
    assert contar_linhas_dados(ROOT / "vendas.csv") == 423


def test_lojas_tem_8_linhas():
    assert contar_linhas_dados(ROOT / "lojas.csv") == 8


def test_receita_lida_como_numero():
    vendas = {v["id_venda"]: v for v in pipeline.ler_vendas()}
    assert len(vendas) == 423
    assert all(isinstance(v["receita_brl"], float) for v in vendas.values())
    assert vendas["V00420"]["receita_brl"] == 349.5
    assert vendas["V00421"]["receita_brl"] == 1200.0


def test_ler_lojas():
    lojas = pipeline.ler_lojas()
    assert len(lojas) == 8
    assert {l["id_loja"] for l in lojas} >= {"101", "108"}
