import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pipeline  # noqa: E402

README = ROOT / "README.md"


@pytest.fixture(scope="module")
def readme():
    pipeline.main()
    return README.read_text(encoding="utf-8")


def test_declara_inner_join(readme):
    assert "inner join" in readme.lower()
    assert "id_loja" in readme
    assert "Motivo" in readme


def test_linhas_entram_e_saem(readme):
    assert "423 linhas entram, 420 saem" in readme


def test_vendas_orfas(readme):
    for id_venda in ["V00421", "V00422", "V00423"]:
        assert id_venda in readme
    assert "id_loja=999" in readme
    assert "R$ 8.120,00" in readme
    assert "939394.06" in readme and "931274.06" in readme


def test_loja_sem_vendas(readme):
    assert "108" in readme and "Batel/PR" in readme


def test_instrucoes(readme):
    assert "python src/pipeline.py" in readme
    assert "python -m pytest -q" in readme


def test_entregaveis_regenerados(readme):
    for nome in ["vendas_lojas.csv", "pivot_receita.csv", "index.html", "README.md"]:
        assert (ROOT / nome).exists()
