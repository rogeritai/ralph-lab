"""Pipeline de vendas: do CSV ao gráfico.

Executar a partir da raiz do repo: python src/pipeline.py
"""
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDAS_CSV = ROOT / "vendas.csv"
LOJAS_CSV = ROOT / "lojas.csv"
VENDAS_LOJAS_CSV = ROOT / "vendas_lojas.csv"
PIVOT_CSV = ROOT / "pivot_receita.csv"
INDEX_HTML = ROOT / "index.html"


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


def calcular_pivot(caminho=VENDAS_LOJAS_CSV):
    """Lê vendas_lojas.csv e soma receita por regiao x mês (YYYY-MM), sem arredondar.

    Devolve (meses, pivot) com meses ordenados e pivot[regiao][mes] = float.
    """
    with open(caminho, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    meses = sorted({linha["data"][:7] for linha in linhas})
    pivot = {}
    for linha in linhas:
        por_mes = pivot.setdefault(linha["regiao"], {m: 0.0 for m in meses})
        por_mes[linha["data"][:7]] += float(linha["receita_brl"])
    return meses, dict(sorted(pivot.items()))


def escrever_pivot(meses, pivot, caminho=PIVOT_CSV):
    """Grava o pivot; arredonda para 2 casas só aqui, na escrita."""
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["regiao", *meses])
        for regiao, por_mes in pivot.items():
            writer.writerow([regiao, *(f"{por_mes[m]:.2f}" for m in meses)])


def formatar_brl(valor):
    """Formata no padrão brasileiro: 931274.06 -> 'R$ 931.274,06'."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def encontrar_anomalias(vendas, lojas):
    """Devolve (vendas órfãs sem loja, lojas sem nenhuma venda)."""
    ids_lojas = {loja["id_loja"] for loja in lojas}
    ids_com_venda = {venda["id_loja"] for venda in vendas}
    orfas = [v for v in vendas if v["id_loja"] not in ids_lojas]
    sem_venda = [l for l in lojas if l["id_loja"] not in ids_com_venda]
    return orfas, sem_venda


def gerar_conclusao(meses, pivot, orfas, sem_venda):
    """Texto de conclusão com valores calculados a partir do pivot e das anomalias."""
    totais = {regiao: sum(por_mes.values()) for regiao, por_mes in pivot.items()}
    total = sum(totais.values())
    lider = max(totais, key=totais.get)
    ids_orfas = ", ".join(v["id_venda"] for v in orfas)
    ids_loja_orfa = ", ".join(sorted({v["id_loja"] for v in orfas}))
    soma_orfas = sum(v["receita_brl"] for v in orfas)
    lojas_txt = ", ".join(
        f"{l['id_loja']} ({l['nome_loja']}/{l['uf']})" for l in sem_venda
    )
    return (
        f"Entre {meses[0]} e {meses[-1]}, a receita total das vendas com loja "
        f"identificada foi de {formatar_brl(total)}. A região líder foi {lider}, "
        f"com {formatar_brl(totais[lider])} no semestre. O relatório usa inner join "
        f"por id_loja, por isso duas anomalias ficam de fora: as {len(orfas)} vendas "
        f"órfãs ({ids_orfas}), com id_loja={ids_loja_orfa}, que não existe no "
        f"cadastro de lojas e somam {formatar_brl(soma_orfas)}, foram excluídas; e a "
        f"loja {lojas_txt}, que não tem nenhuma venda registrada, não aparece no "
        f"gráfico nem nas tabelas."
    )


def escrever_index(meses, pivot, conclusao, caminho=INDEX_HTML):
    """Gera a página estática com o gráfico Chart.js e o parágrafo de conclusão."""
    dados = {
        "labels": meses,
        "datasets": [
            {"label": regiao, "data": [round(por_mes[m], 2) for m in meses]}
            for regiao, por_mes in pivot.items()
        ],
    }
    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Receita mensal por região</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<h1>Receita mensal por região ({meses[0]} a {meses[-1]})</h1>
<canvas id="grafico"></canvas>
<p>{html.escape(conclusao)}</p>
<script>
const dados = {json.dumps(dados, ensure_ascii=False)};
new Chart(document.getElementById("grafico"), {{
  type: "line",
  data: dados,
  options: {{
    scales: {{ y: {{ title: {{ display: true, text: "Receita (R$)" }} }} }}
  }}
}});
</script>
</body>
</html>
"""
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write(pagina)


def main():
    vendas = ler_vendas()
    lojas = ler_lojas()
    print(f"vendas.csv: {len(vendas)} linhas | lojas.csv: {len(lojas)} linhas")
    juntas = juntar_vendas_lojas(vendas, lojas)
    escrever_vendas_lojas(juntas)
    print(f"vendas_lojas.csv: {len(juntas)} linhas (inner join por id_loja)")
    meses, pivot = calcular_pivot()
    escrever_pivot(meses, pivot)
    print(f"pivot_receita.csv: {len(pivot)} regiões x {len(meses)} meses")
    orfas, sem_venda = encontrar_anomalias(vendas, lojas)
    escrever_index(meses, pivot, gerar_conclusao(meses, pivot, orfas, sem_venda))
    print("index.html: gráfico + conclusão")


if __name__ == "__main__":
    main()
