# PRD: Pipeline de vendas — do CSV ao gráfico

## Introdução

Construir, em Python, um pipeline de dados que parte de dois CSVs de origem na raiz do repositório (`vendas.csv` e `lojas.csv`) e produz três entregáveis, também na raiz: o join das duas tabelas (`vendas_lojas.csv`), um pivot de receita por região × mês (`pivot_receita.csv`) e uma página estática com gráfico e conclusão (`index.html`). Um `README.md` documenta a decisão de join e seu efeito sobre os dados.

O pipeline será construído pelo laço autônomo Ralph: cada user story abaixo deve caber em uma única iteração, e "pronto" é definido pela suíte `pytest` inteira verde.

### Dados de origem

- `vendas.csv` — 423 linhas de dados. Colunas: `id_venda, data, id_loja, categoria, unidades, receita_brl`. `data` está no formato `YYYY-MM-DD`, de 2026-01 a 2026-06. `receita_brl` é decimal com ponto, sem zeros à direita (há valores como `349.5` e `1200`).
- `lojas.csv` — 8 linhas de dados. Colunas: `id_loja, nome_loja, regiao, uf, gerente`. Regiões: `Centro-Oeste`, `Nordeste`, `Sudeste`, `Sul`.

### Anomalias propositais (não são bugs)

1. **Três vendas órfãs**: `V00421`, `V00422` e `V00423` têm `id_loja=999`, que não existe em `lojas.csv`. Somam R$ 8.120,00.
2. **Loja sem vendas**: a loja 108 (Batel/PR) existe em `lojas.csv` e não aparece em `vendas.csv`.

A decisão deste projeto é usar **inner join**: as 3 vendas órfãs e a loja 108 ficam fora do relatório, e isso é documentado no `README.md`.

## Objetivos

- Gerar `vendas_lojas.csv` com exatamente 420 linhas de dados e soma de `receita_brl` igual a 931274.06.
- Gerar `pivot_receita.csv` no formato exato exigido (4 regiões × 6 meses), com soma das células igual a 931274.06.
- Gerar `index.html` com um gráfico da receita mensal por região e um parágrafo de conclusão de pelo menos 300 caracteres.
- Documentar no `README.md` a escolha do inner join e o que ficou de fora.
- Ter a suíte `python -m pytest -q` verde, com pelo menos 4 testes em `tests/test_*.py`.
- Todos os números das saídas são calculados pelo pipeline a partir dos CSVs de origem, nunca digitados à mão.

## User Stories

### US-001: Estrutura do projeto e testes iniciais
**Descrição:** Como desenvolvedor, quero a estrutura do projeto e um primeiro teste rodando, para que as próximas iterações tenham onde colocar código e como verificar o resultado.

**Critérios de aceitação:**
- [ ] Existe `src/pipeline.py`, executável com `python src/pipeline.py` a partir da raiz do repo, com funções de leitura de `vendas.csv` e `lojas.csv` usando o módulo `csv` e `encoding="utf-8"`
- [ ] A leitura converte `receita_brl` para número (não texto); valores como `349.5` e `1200` são lidos corretamente
- [ ] Existe `tests/test_origem.py` verificando que `vendas.csv` tem 423 linhas de dados e `lojas.csv` tem 8 linhas de dados
- [ ] Os testes localizam os arquivos pela raiz do repo (a partir de `__file__`), sem depender do diretório corrente
- [ ] `vendas.csv` e `lojas.csv` não foram modificados
- [ ] `python -m pytest -q` passa

### US-002: Join de vendas com lojas
**Descrição:** Como analista, quero cada venda acompanhada dos dados da sua loja, para poder agregar a receita por região.

**Critérios de aceitação:**
- [ ] `python src/pipeline.py` gera `vendas_lojas.csv` na raiz do repo
- [ ] O arquivo é o inner join de `vendas.csv` com `lojas.csv` por `id_loja`
- [ ] O arquivo tem exatamente 420 linhas de dados (mais 1 de cabeçalho)
- [ ] O arquivo mantém a coluna com o nome exato `receita_brl` e inclui a coluna `regiao`
- [ ] As vendas `V00421`, `V00422` e `V00423` (`id_loja=999`) não aparecem no arquivo
- [ ] Existe teste em `tests/` verificando que `vendas_lojas.csv` tem 420 linhas de dados
- [ ] Existe teste em `tests/` verificando que a soma de `receita_brl` em `vendas_lojas.csv` é 931274.06 (tolerância 0,50)
- [ ] `vendas.csv` e `lojas.csv` não foram modificados
- [ ] `python -m pytest -q` passa

### US-003: Pivot de receita por região × mês
**Descrição:** Como gestor, quero a receita de cada região em cada mês numa tabela, para comparar o desempenho das regiões ao longo do semestre.

**Critérios de aceitação:**
- [ ] `python src/pipeline.py` gera `pivot_receita.csv` na raiz do repo, calculado a partir de `vendas_lojas.csv`
- [ ] O cabeçalho é exatamente `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`
- [ ] Há 4 linhas de dados em ordem alfabética: `Centro-Oeste`, `Nordeste`, `Sudeste`, `Sul`; cada linha tem 7 colunas
- [ ] O mês de cada venda vem dos 7 primeiros caracteres da coluna `data` (`YYYY-MM`)
- [ ] Os valores usam ponto como separador decimal e 2 casas (exemplo de formato: `12345.67`), sem `R$` e sem separador de milhar
- [ ] O arredondamento acontece só na escrita do CSV, nunca nas somas parciais
- [ ] Existe teste em `tests/` verificando: cabeçalho exato, 4 linhas × 7 colunas, soma de todas as células numéricas igual a 931274.06 (tolerância 0,50) e `Sudeste` como região de maior receita, com total 265077.49 (tolerância 0,50)
- [ ] `python -m pytest -q` passa

### US-004: Página index.html com gráfico e conclusão
**Descrição:** Como leitor do relatório, quero uma página com o gráfico da receita mensal por região e uma conclusão escrita, para entender o resultado sem abrir os CSVs.

**Critérios de aceitação:**
- [ ] `python src/pipeline.py` gera `index.html` na raiz do repo
- [ ] A página é estática e contém um elemento `<canvas>` com um gráfico Chart.js (carregado via CDN) da receita mensal por região: uma série por região, meses de 2026-01 a 2026-06 no eixo X
- [ ] Os dados do gráfico estão embutidos na própria página e vêm do pivot calculado pelo pipeline (não digitados à mão)
- [ ] A página contém um `<p>` de conclusão, em português, com pelo menos 300 caracteres
- [ ] A conclusão cita a receita total (R$ 931.274,06), a região líder (Sudeste, R$ 265.077,49) e o tratamento das duas anomalias (3 vendas órfãs com `id_loja=999` e a loja 108 sem vendas); os valores citados são calculados pelo pipeline e formatados no padrão brasileiro
- [ ] O arquivo é escrito com `encoding="utf-8"` e declara `<meta charset="utf-8">`
- [ ] Existe teste em `tests/` verificando que `index.html` contém um `<canvas>` e um `<p>` com 300 ou mais caracteres de texto
- [ ] `python -m pytest -q` passa

### US-005: README com a documentação das anomalias
**Descrição:** Como avaliador, quero ler qual join foi escolhido e o que ele deixou de fora, para saber que a perda de dados foi uma decisão registrada e não um descuido.

**Critérios de aceitação:**
- [ ] Existe `README.md` na raiz do repo, em português
- [ ] O README declara que o join usado é o inner join por `id_loja` e explica o motivo
- [ ] O README informa: 423 linhas entram, 420 saem
- [ ] O README informa que as 3 vendas órfãs (`V00421`, `V00422`, `V00423`, `id_loja=999`) ficam de fora e somam R$ 8.120,00, e que a receita total cai de 939394.06 para 931274.06
- [ ] O README informa que a loja 108 (Batel/PR) não aparece no relatório por não ter vendas
- [ ] O README explica como regenerar os entregáveis (`python src/pipeline.py`) e como rodar os testes (`python -m pytest -q`)
- [ ] `python src/pipeline.py` roda do zero sem erro e regenera os três entregáveis
- [ ] `vendas.csv` e `lojas.csv` não foram modificados
- [ ] `python -m pytest -q` passa, com pelo menos 4 testes no total

## Requisitos Funcionais

- FR-1: O pipeline deve ler `vendas.csv` e `lojas.csv` da raiz do repo com o módulo `csv` da biblioteca padrão.
- FR-2: O pipeline deve tratar `receita_brl` como número em todos os cálculos.
- FR-3: O pipeline deve produzir `vendas_lojas.csv` na raiz, como inner join por `id_loja`, com 420 linhas de dados, preservando o nome da coluna `receita_brl` e incluindo `regiao`.
- FR-4: O pipeline deve produzir `pivot_receita.csv` na raiz, a partir de `vendas_lojas.csv`, com cabeçalho exato `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06` e 4 linhas de dados em ordem alfabética de região.
- FR-5: Os valores do pivot devem ser escritos com ponto decimal e 2 casas, sem símbolo de moeda e sem separador de milhar; o arredondamento ocorre só na escrita.
- FR-6: O pipeline deve produzir `index.html` na raiz, com um `<canvas>` Chart.js da receita mensal por região e um `<p>` de conclusão com 300 ou mais caracteres.
- FR-7: Um único comando, `python src/pipeline.py`, executado da raiz, deve regenerar os três entregáveis.
- FR-8: A suíte em `tests/test_*.py` deve ter pelo menos 4 testes cobrindo: linhas do join, receita total do join, forma e total do pivot, e presença do gráfico e da conclusão na página.
- FR-9: O `README.md` deve documentar a escolha do inner join, as contagens de linhas e a receita excluída.

## Fora de Escopo

- Não editar, limpar, reordenar nem apagar linhas de `vendas.csv` e `lojas.csv`: eles são somente leitura.
- Não inventar dados nem escrever os números esperados à mão nos entregáveis; os valores de conferência aparecem só nos testes e no README.
- Não usar pandas nem outra dependência além da biblioteca padrão e do pytest.
- Não produzir left join, nem linha de região nula, nem linha para a loja 108 no pivot.
- Não criar servidor web, build de front-end ou verificação em navegador.
- Não alterar `scripts/ralph/ralph.sh` nem `scripts/ralph/CLAUDE.md`.
- Não colocar os entregáveis em subpastas como `data/` ou `web/`.

## Considerações Técnicas

- Python 3.13 no Windows com Git Bash: usar o comando `python`, não `python3`.
- Abrir arquivos sempre com `encoding="utf-8"`; na escrita de CSV, usar também `newline=""` para não gerar linhas em branco no Windows.
- O código do pipeline fica em `src/` (por exemplo `src/pipeline.py`); os testes ficam em `tests/` e leem os entregáveis da raiz do repo.
- Os testes verificam os arquivos gerados; antes de rodar a suíte, executar `python src/pipeline.py` para que os entregáveis estejam atualizados. Os entregáveis gerados são versionados no repositório.
- Não há typecheck nem lint configurados: a verificação de qualidade de cada story é `python -m pytest -q`.
- Não há interface a verificar em navegador; a página é validada só pelo pytest.

## Métricas de Sucesso

- `vendas_lojas.csv`: 420 linhas de dados; soma de `receita_brl` = 931274.06 (tolerância 0,50).
- `pivot_receita.csv`: cabeçalho exato, 4 linhas × 7 colunas; soma das células = 931274.06 (tolerância 0,50); Sudeste líder com 265077.49.
- `index.html`: contém `<canvas>` e `<p>` de conclusão com 300 ou mais caracteres.
- `python -m pytest -q`: pelo menos 4 testes passando e nenhum falhando.
- `vendas.csv` continua com 423 linhas de dados e `lojas.csv` com 8.

## Questões em Aberto

Nenhuma. As decisões de join, formato e ferramentas estão fechadas acima.
