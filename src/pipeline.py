"""Pipeline de vendas: do CSV ao gráfico.

Executar a partir da raiz do repo: python src/pipeline.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDAS_CSV = ROOT / "vendas.csv"
LOJAS_CSV = ROOT / "lojas.csv"
VENDAS_LOJAS_CSV = ROOT / "vendas_lojas.csv"


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


def juntar_vendas_lojas(vendas, lojas):
    """Inner join por id_loja: vendas sem loja (órfãs) e lojas sem venda ficam de fora."""
    por_id = {loja["id_loja"]: loja for loja in lojas}
    juntas = []
    for venda in vendas:
        loja = por_id.get(venda["id_loja"])
        if loja is None:
            continue
        linha = dict(venda)
        for campo, valor in loja.items():
            if campo != "id_loja":
                linha[campo] = valor
        juntas.append(linha)
    return juntas


def escrever_vendas_lojas(linhas, caminho=VENDAS_LOJAS_CSV):
    """Grava o resultado do join; receita_brl sai com ponto decimal e 2 casas."""
    campos = list(linhas[0].keys())
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for linha in linhas:
            saida = dict(linha)
            saida["receita_brl"] = f"{linha['receita_brl']:.2f}"
            writer.writerow(saida)


def main():
    vendas = ler_vendas()
    lojas = ler_lojas()
    print(f"vendas.csv: {len(vendas)} linhas | lojas.csv: {len(lojas)} linhas")
    juntas = juntar_vendas_lojas(vendas, lojas)
    escrever_vendas_lojas(juntas)
    print(f"vendas_lojas.csv: {len(juntas)} linhas (inner join por id_loja)")


if __name__ == "__main__":
    main()
