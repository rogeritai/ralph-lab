"""Pipeline de vendas: do CSV ao gráfico.

Executar a partir da raiz do repo: python src/pipeline.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDAS_CSV = ROOT / "vendas.csv"
LOJAS_CSV = ROOT / "lojas.csv"


def ler_vendas(caminho=VENDAS_CSV):
    """Lê vendas.csv; receita_brl vira float e unidades vira int."""
    with open(caminho, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    for linha in linhas:
        linha["receita_brl"] = float(linha["receita_brl"])
        linha["unidades"] = int(linha["unidades"])
    return linhas


def ler_lojas(caminho=LOJAS_CSV):
    """Lê lojas.csv como lista de dicionários."""
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    vendas = ler_vendas()
    lojas = ler_lojas()
    print(f"vendas.csv: {len(vendas)} linhas | lojas.csv: {len(lojas)} linhas")


if __name__ == "__main__":
    main()
