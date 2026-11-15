# Pipeline de vendas: do CSV ao gráfico

> Este arquivo é gerado por `python src/pipeline.py`; os números abaixo são
> calculados pelo pipeline a partir de `vendas.csv` e `lojas.csv`.

## Entregáveis

- `vendas_lojas.csv`: cada venda com os dados da sua loja (join por `id_loja`).
- `pivot_receita.csv`: receita por região x mês.
- `index.html`: gráfico Chart.js da receita mensal por região e conclusão.

## Decisão de join

O join usado é o **inner join por `id_loja`** entre `vendas.csv` e `lojas.csv`.

Motivo: o relatório agrega a receita por região, e a região vem do cadastro de
lojas. Uma venda sem loja cadastrada não tem região, então não há onde colocá-la
no pivot nem no gráfico; e uma loja sem vendas não contribui com receita. O inner
join mantém só as linhas que têm os dois lados, sem inventar uma região para as
vendas órfãs. A perda de dados é intencional e está registrada abaixo.

## O que fica de fora

- Linhas: **423 linhas entram, 420 saem**.
- Vendas órfãs: as 3 vendas V00421, V00422, V00423 (id_loja=999),
  cujo id_loja não existe em `lojas.csv`, ficam de fora e somam
  **R$ 8.120,00**.
- Receita total: cai de **939394.06** (todas as vendas) para
  **931274.06** (vendas com loja identificada).
- Loja 108 (Batel/PR): não aparece no relatório por não ter vendas.

## Como usar

Regenerar os entregáveis (a partir da raiz do repo):

```
python src/pipeline.py
```

Rodar os testes:

```
python -m pytest -q
```

Requisitos: Python 3.13 (só biblioteca padrão) e pytest.
