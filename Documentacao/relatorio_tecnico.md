---
output:
  pdf_document: default
  html_document: default
---
# Relatório — Projeto Final de Banco de Dados
**Disciplina:** Banco de Dados — DCC/UFMG  
**Professor:** Pedro H. Barros  
**Dataset:** Oscar AMPAS — Winner Demographics (1927–2014)

---

## 1. Introdução

Este projeto implementa o ciclo completo de um banco de dados relacional sobre os vencedores do Oscar (Academy Awards), premiação anual da Academia de Artes e Ciências Cinematográficas dos Estados Unidos (AMPAS). O dataset contém informações demográficas de vencedores de cinco categorias principais entre 1927 e 2014, permitindo análises sobre representatividade étnica, longevidade de carreira e domínio artístico ao longo de quase nove décadas de cinema.

### Motivação
O Oscar é a premiação cinematográfica mais influente do mundo. Analisar o perfil dos vencedores ao longo do tempo revela padrões históricos de diversidade — ou ausência dela — na indústria do cinema.

---

## 2. Dataset

| Atributo | Valor |
|---|---|
| Fonte | FiveThirtyEight / AMPAS |
| Arquivo | `world_ampas_oscar_winner_demographics.csv` |
| Linhas | 415 |
| Colunas | 10 |
| Período | 1927 a 2014 |

### Colunas originais

| Coluna | Tipo | Descrição |
|---|---|---|
| name | texto | Nome do vencedor |
| birth_year | inteiro | Ano de nascimento |
| birth_date | data | Data de nascimento |
| birthplace | texto | Local de nascimento (texto livre) |
| race_ethnicity | texto | Etnia (6 valores: White, Black, Hispanic, Asian, Multiracial, Middle Eastern) |
| religion | texto | Religião — 62% ausente |
| sexual_orientation | texto | Orientação sexual — "Na" tratado como NULL |
| year_edition | inteiro | Ano da cerimônia |
| category | texto | Categoria do Oscar (5 categorias) |
| movie | texto | Filme premiado |

### Tratamento de dados ausentes
- `religion`: 62% de ausência estrutural — dado não coletado para todos os vencedores históricos. Tratado como `NULL`.
- `sexual_orientation`: string `"Na"` convertida para `NULL` na carga.
- `birth_date`: 1 registro ausente; `birth_year` mantido para não perder informação.

---

## 3. Modelo Entidade-Relacionamento

### Entidades

| Entidade | Atributos | Chave |
|---|---|---|
| VENCEDOR | nome, ano_nascimento, data_nascimento, local_nascimento, etnia, religiao, orient_sexual | id_vencedor |
| FILME | titulo | id_filme |
| CATEGORIA | nome | id_categoria |
| EDICAO | ano | id_edicao |
| PREMIO | — (somente FKs) | id_premio |

### Relacionamentos
- `PREMIO` é uma **entidade associativa** que conecta as quatro dimensões.
- Todos os relacionamentos são **N:1** de PREMIO para as demais entidades.
- Um vencedor pode ter múltiplos prêmios (ex: Katharine Hepburn — 4 Oscars).
- Um filme pode vencer múltiplas categorias na mesma edição.

### Diagrama ER
Gerado via dbdiagram.io a partir do arquivo `Etapa1_ModeloER/diagrama_er.dbml`.

---

## 4. Modelo Relacional

```
vencedor(id_vencedor PK, nome, ano_nascimento, data_nascimento,
         local_nascimento, etnia, religiao, orient_sexual)

filme(id_filme PK, titulo)

categoria(id_categoria PK, nome)

edicao(id_edicao PK, ano)

premio(id_premio PK,
       id_vencedor FK → vencedor,
       id_filme    FK → filme,
       id_categoria FK → categoria,
       id_edicao   FK → edicao)
```

### Normalização

**1FN:** todos os valores são atômicos. `local_nascimento` é texto livre, mas atômico por linha.

**2FN:** todas as tabelas têm chave primária simples — dependências parciais são impossíveis.

**3FN:** único caso analisado foi `ano_nascimento` vs `data_nascimento` em VENCEDOR. Optou-se por manter ambos pois há 1 registro com `birth_year` mas sem `birth_date` completa — eliminar a coluna causaria perda real de informação. Não há dependências transitivas nas demais tabelas.

---

## 5. Implementação Física

### Banco de dados
- **SGBD:** PostgreSQL 16 (via Docker)
- **Container:** `oscar-db`
- **Banco:** `oscar`

### Constraints implementadas

| Constraint | Tipo | Tabela |
|---|---|---|
| `id_*` únicos e não nulos | Chave primária | Todas |
| `nome` NOT NULL | Entidade | vencedor, filme, categoria |
| `ano >= 1927` | Domínio | edicao |
| FKs referenciam registros existentes | Referencial | premio |
| `(id_vencedor, id_categoria, id_edicao)` único | Negócio | premio |

### Índices criados
```sql
CREATE INDEX idx_premio_vencedor  ON premio(id_vencedor);
CREATE INDEX idx_premio_filme     ON premio(id_filme);
CREATE INDEX idx_premio_categoria ON premio(id_categoria);
CREATE INDEX idx_premio_edicao    ON premio(id_edicao);
```

---

## 6. Carga dos Dados

Pipeline em Python (`Etapa3_SQL/02_carga_dados.py`) usando `psycopg2`.

**Ordem de inserção:**
1. `edicao` — 87 cerimônias
2. `categoria` — 5 categorias
3. `filme` — 335 títulos únicos
4. `vencedor` — 348 pessoas únicas (deduplicadas por nome)
5. `premio` — 415 registros (um por linha do CSV)

**Validação pós-carga:**
- Zero registros órfãos em todas as FKs
- Nenhuma duplicata na constraint `uq_premio`
- NULLs distribuídos como esperado (`religion`: 219, `orient_sexual`: 10)

---

## 7. Análise Exploratória

### P1 — Filmes com múltiplas vitórias na mesma edição
*It Happened One Night* (1935), *Gone with the Wind* (1940) e *Going My Way* (1945) foram os únicos a vencer 3 categorias em uma mesma cerimônia. 60 filmes no total venceram 2 ou mais categorias.

### P2 — Diversidade étnica por década
Até os anos 1970, a proporção de vencedores não-brancos foi praticamente zero. A partir dos anos 2000, subiu para cerca de 19%, ainda longe de representar a diversidade da população americana.

### P3 — Idade dos vencedores
Atrizes vencem mais jovens (média 37 anos) enquanto atores coadjuvantes vencem mais velhos (média 51). A mais jovem foi Tatum O'Neal com 11 anos (1974); o mais velho foi Christopher Plummer com 83 anos (2012).

### P4 — Intervalo entre vitórias
Helen Hayes esperou 39 anos entre seu primeiro (1932) e segundo Oscar (1971), o maior intervalo registrado. Katharine Hepburn também esperou 34 anos (1934–1968).

### P5 — Primeira vitória não-branca por categoria
| Categoria | Vencedor | Etnia | Ano |
|---|---|---|---|
| Best Supporting Actress | Hattie McDaniel | Black | 1940 |
| Best Actor | Jose Ferrer | Hispanic | 1951 |
| Best Supporting Actor | Anthony Quinn | Hispanic | 1953 |
| Best Actress | Halle Berry | Multiracial | 2002 |
| Best Director | Ang Lee | Asian | 2006 |

---

## 8. Conclusão

O projeto implementou com sucesso todas as etapas do ciclo de vida de um banco de dados relacional: modelagem ER, mapeamento relacional, normalização até 3FN, implementação DDL com restrições de integridade, pipeline de carga e análise exploratória via SQL e visualizações.

Os dados revelam que a Academia de Artes e Ciências Cinematográficas demorou décadas para reconhecer artistas não-brancos, com a primeira vitória não-branca em Best Director ocorrendo apenas em 2006 — quase 80 anos após a primeira cerimônia.

---

## Arquivos do Projeto

```
Documentacao/
├── Etapa0_Exploracao/01_exploracao.ipynb
├── Etapa1_ModeloER/diagrama_er.dbml
├── Etapa3_SQL/
│   ├── 01_ddl_criar_tabelas.sql
│   ├── 02_carga_dados.py
│   └── 03_validacao_carga.sql
└── Etapa4_EDA/
    ├── 04_perguntas_investigativas.md
    ├── 05_consultas_sql.sql
    └── 06_visualizacoes.ipynb

Aprendizado/
├── 00_rota_do_projeto.md
├── 01_entidades_regras.md
└── 02_modelo_relacional_normalizacao.md
```
