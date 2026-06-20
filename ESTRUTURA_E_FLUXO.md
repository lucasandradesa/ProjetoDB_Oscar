# Estrutura e Fluxo de Execução — Projeto Final de Banco de Dados

**Disciplina:** Banco de Dados — DCC/UFMG  
**Dataset:** Oscar AMPAS Winner Demographics (1927–2014)

---

## Visão Geral das Pastas

```
projetoFinalDB/
│
├── world_ampas_oscar_winner_demographics.csv   ← dataset original
│
├── Documentacao/                               ← entregas do projeto (código, SQL, gráficos)
│   ├── Etapa1_ModeloER/
│   ├── Etapa3_SQL/
│   ├── Etapa4_EDA/
│   ├── relatorio_tecnico.md
│   └── apresentacao_oscar.pptx
│
├── Aprendizado/                                ← registros de decisões e contexto
│   ├── 01_entidades_regras.md
│   ├── 02_modelo_relacional_normalizacao.md
│   ├── grafico_oscar_exploracao.png
│
└── .vscode/                                    ← configurações do editor (ignorar)
```

---

## Arquivos na Raiz

### `world_ampas_oscar_winner_demographics.csv`
Fonte dos dados brutos. Contém 415 linhas e 10 colunas:

| Coluna | Conteúdo |
|---|---|
| `name` | Nome do vencedor |
| `birth_year` | Ano de nascimento |
| `birth_date` | Data de nascimento completa |
| `birthplace` | Texto livre (cidade, estado, país) |
| `race_ethnicity` | Etnia — 6 valores: White, Black, Hispanic, Asian, Multiracial, Middle Eastern |
| `religion` | Religião — 62% ausente (NULL estrutural) |
| `sexual_orientation` | Orientação sexual — string `"Na"` tratada como NULL |
| `year_edition` | Ano da cerimônia Oscar |
| `category` | Categoria premiada (5 categorias fixas) |
| `movie` | Título do filme premiado |

Este arquivo é lido **somente pelo script `02_carga_dados.py`**. Nenhum outro arquivo o acessa diretamente.

---

## Pasta `Documentacao/`

Contém todas as entregas formais do projeto, organizadas por etapa de criação e desenvolvimento.

---

#### `01_exploracao.ipynb`
Notebook Jupyter de exploração inicial do dataset. É o **primeiro arquivo a ser executado** no projeto.

**Objetivo:** entender o dataset antes de modelar o banco.

**O que faz, célula a célula:**
1. Instala dependências (`pandas`, `matplotlib`) se necessário
2. Lê `world_ampas_oscar_winner_demographics.csv` com `pd.read_csv()`
3. Exibe `df.shape`, `df.dtypes`, `df.head()` — visão geral
4. Conta valores nulos por coluna — (revela 62% de ausência em `religion`)
5. Identifica `"Na"` em `sexual_orientation` como string especial (não NULL real)
6. Calcula cardinalidades: edições únicas (87), categorias (5), filmes (335), vencedores (348)
7. Plota distribuições: prêmios por etnia, prêmios por categoria, prêmios por década
8. Salva gráfico exploratório em `Aprendizado/grafico_oscar_exploracao.png`

**Não modifica o banco.** Serve apenas para análise e tomada de decisão de modelagem.

---

### `Etapa1_ModeloER/`

#### `diagrama_er.dbml`
Definição do diagrama ER em DBML (Database Markup Language), formato usado pelo site para geração autmática do diagrama visual pelo site: [dbdiagram.io](https://dbdiagram.io).

**Conteúdo:** define 5 tabelas (`vencedor`, `filme`, `categoria`, `edicao`, `premio`) com seus campos, tipos e relacionamentos (FKs).

**Como fizemos:** copiamos o conteúdo e colamos no editor de [dbdiagram.io](https://dbdiagram.io) para gerar o diagrama visualmente.

**Não é executado diretamente.** É um arquivo de documentação/modelagem.

#### `oscar.png` e `oscar.svg`
Imagens exportadas do diagrama ER gerado no dbdiagram.io.
---

### `Etapa3_SQL/`

Aqui temos três scripts que implementam e preenchem o banco. **Devem ser executados nesta ordem:**

```
01_ddl_criar_tabelas.sql  →  02_carga_dados.py  →  03_validacao_carga.sql
```

---

#### `01_ddl_criar_tabelas.sql`
Script SQL que cria o esquema físico do banco de dados.

**Como executar** (com o container Docker `oscar-db` rodando):
```powershell
docker cp "Documentacao\Etapa3_SQL\01_ddl_criar_tabelas.sql" oscar-db:/tmp/ddl.sql
docker exec oscar-db psql -U postgres -d oscar -f /tmp/ddl.sql
```

**O que faz, em ordem:**
1. Remove (DROP CASCADE) todas as tabelas existentes — permite re-execução limpa
2. Cria `edicao` — chave primária `SERIAL`, constraint `ano >= 1927`
3. Cria `categoria` — chave primária `SERIAL`, nome único
4. Cria `filme` — chave primária `SERIAL`, título único
5. Cria `vencedor` — chave primária `SERIAL`, `etnia NOT NULL`, campos demográficos opcionais
6. Cria `premio` — tabela central com 4 FKs obrigatórias + constraint `UNIQUE(id_vencedor, id_categoria, id_edicao)`
7. Cria 4 índices em `premio` para acelerar JOINs nas consultas analíticas

**Pré-requisito:** banco `oscar` deve existir no PostgreSQL. Para criar:
```powershell
docker exec oscar-db psql -U postgres -c "CREATE DATABASE oscar;"
```

---

#### `02_carga_dados.py`
Pipeline Python que lê o CSV e insere os dados no banco na ordem correta.

**Como executar:**
```bash
python "Documentacao\Etapa3_SQL\02_carga_dados.py"
```

**Pré-requisito:** `01_ddl_criar_tabelas.sql` já executado; container `oscar-db` rodando na porta `5432`.

**Fluxo interno:**
```
CSV → pandas DataFrame → limpeza → psycopg2 → PostgreSQL
```

**Etapas detalhadas:**
1. Instala `psycopg2-binary` e `pandas` automaticamente se ausentes
2. Lê o CSV com `pd.read_csv()` — 415 linhas
3. **Limpeza:** substitui `"Na"` por `None` em `sexual_orientation`; converte `birth_date` para datetime
4. Conecta ao banco `oscar` (host: localhost, porta: 5432, usuário: postgres)
5. Insere `edicao` — 87 registros (anos únicos de `year_edition`), usa `ON CONFLICT DO NOTHING`
6. Insere `categoria` — 5 registros (valores únicos de `category`), usa `ON CONFLICT DO NOTHING`
7. Insere `filme` — 335 registros (títulos únicos de `movie`), usa `ON CONFLICT DO NOTHING`
8. Insere `vencedor` — **deduplica por nome** antes de inserir (348 pessoas únicas); converte NaN → None para campos opcionais
9. Monta dicionários `{valor_original: id_gerado}` para cada dimensão
10. Insere `premio` — 415 registros; cada linha do CSV vira 1 prêmio com as 4 FKs resolvidas pelos dicionários
11. Faz `commit()` após cada tabela; em caso de erro, `rollback()` e relança exceção

**Por que a ordem importa:** `premio` referencia as outras 4 tabelas via FK. Inserir `premio` antes das dimensões causaria violação de integridade referencial.

---

#### `03_validacao_carga.sql`
Script SQL com 8 verificações de integridade pós-carga. Deve ser executado após `02_carga_dados.py`.

**Como executar:**
```powershell
docker cp "Documentacao\Etapa3_SQL\03_validacao_carga.sql" oscar-db:/tmp/val.sql
docker exec oscar-db psql -U postgres -d oscar -f /tmp/val.sql
```

**Verificações realizadas:**

| # | O que verifica | Resultado esperado |
|---|---|---|
| 1 | Contagem de linhas por tabela | 87 / 5 / 335 / 348 / 415 |
| 2 | Prêmios sem FK válida (vencedor, filme, categoria, edição) | 0 em todos |
| 3 | Duplicatas na constraint `uq_premio` | Nenhuma linha |
| 4 | Contagem de NULLs em `religion` e `orient_sexual` | 219 e 10 |
| 5 | Vencedores com mais de 1 Oscar | Katharine Hepburn (4), etc. |
| 6 | Categorias distintas — deve ser exatamente 5 | 5 linhas |
| 7 | Distribuição de vencedores por etnia | White dominante, outros menores |
| 8 | Edições com ≠ 5 prêmios | 30 edições (estrutural — décadas iniciais) |

### `Etapa4_EDA/`

Contém as perguntas investigativas, as consultas SQL correspondentes e o notebook de visualizações.

---

#### `04_perguntas_investigativas.md`
Documento de texto com as 5 perguntas investigativas formuladas antes de escrever o SQL. Define para cada pergunta: o enunciado, a técnica SQL usada e a motivação analítica.

**Não é executado.** É documentação de raciocínio.

---

#### `05_consultas_sql.sql`
Arquivo SQL com as 6 consultas analíticas (P1, P2, P3a, P3b, P4, P5).

**Como executar:**
```powershell
docker cp "Documentacao\Etapa4_EDA\05_consultas_sql.sql" oscar-db:/tmp/eda.sql
docker exec oscar-db psql -U postgres -d oscar -f /tmp/eda.sql
```

**Consultas e técnicas:**

| Consulta | Pergunta | Técnica principal |
|---|---|---|
| P1 | Filmes com múltiplas vitórias na mesma edição | JOIN + GROUP BY + HAVING + STRING_AGG |
| P2 | Diversidade étnica por década | GROUP BY + FILTER + divisão percentual |
| P3a | Idade média por categoria | AVG / MIN / MAX por grupo |
| P3b | 5 mais jovens e 5 mais velhos | UNION ALL + ORDER BY com expressão (não alias) |
| P4 | Maior intervalo entre vitórias consecutivas | CTE + window function LAG |
| P5 | Primeiro vencedor não-branco por categoria | CTE + ROW_NUMBER() OVER (PARTITION BY categoria) |

**Pré-requisito:** banco populado por `02_carga_dados.py`.

---

#### `06_visualizacoes.ipynb`
Notebook Jupyter que conecta ao banco PostgreSQL e gera 5 gráficos PNG.

**Como executar:** abrir no Jupyter e executar todas as células em sequência.

**Pré-requisito:** banco populado; container `oscar-db` rodando.

**Fluxo célula a célula:**
1. Instala `psycopg2-binary`, `pandas`, `matplotlib`
2. Define conexão com o banco e função `query(sql)` — executa SQL e retorna DataFrame
3. **P1** — busca os 15 filmes com mais categorias vencidas na mesma edição; plota barras horizontais douradas; salva `grafico_p1_filmes_multivencedores.png`
4. **P2** — busca total e % não-brancos por década; plota barras empilhadas (azul claro/azul) + linha vermelha de percentual (eixo Y duplo); salva `grafico_p2_diversidade_decada.png`
5. **P3** — busca idade média, mínima e máxima por categoria; plota barras com error bars (min–max); salva `grafico_p3_idade_categoria.png`
6. **P4** — usa a query CTE+LAG para buscar os 10 maiores intervalos; plota barras horizontais verdes; salva `grafico_p4_intervalo_vitorias.png`
7. **P5** — busca o primeiro vencedor não-branco por categoria; plota gráfico de dispersão (scatter) com anotações de nome e etnia; salva `grafico_p5_primeira_vitoria_nao_branca.png`

**Arquivos gerados**:
- `grafico_p1_filmes_multivencedores.png`
- `grafico_p2_diversidade_decada.png`
- `grafico_p3_idade_categoria.png`
- `grafico_p4_intervalo_vitorias.png`
- `grafico_p5_primeira_vitoria_nao_branca.png`

## Pré-requisitos para Reprodução

| Requisito | Versão usada |
|---|---|
| Python | 3.x |
| PostgreSQL | 16 (via Docker) |
| Docker | qualquer versão recente |
| pandas | qualquer versão recente |
| psycopg2-binary | qualquer versão recente |
| matplotlib | qualquer versão recente |
| python-pptx | qualquer versão recente |
| Jupyter Notebook / JupyterLab | para abrir `.ipynb` |

**Iniciar o container Docker:**
```powershell
docker start oscar-db
# aguardar ~3 segundos para o PostgreSQL inicializar
```

**Credenciais do banco:**
- Host: `localhost`
- Porta: `5432`
- Banco: `oscar`
- Usuário: `postgres`
- Senha: `brasil123`
