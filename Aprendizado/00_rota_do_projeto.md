# Rota do Projeto — Oscar AMPAS Winner Demographics

## Dataset
- **Fonte:** FiveThirtyEight / AMPAS
- **Arquivo:** `world_ampas_oscar_winner_demographics.csv`
- **Escopo:** Vencedores de 5 categorias principais, 1927–2014 (415 registros)

## Estrutura de Pastas
```
projetoFinalDB/
├── Apresentacao/                  ← slides para sala
├── Documentacao/
│   ├── Etapa0_Exploracao/         ← notebook de exploração
│   ├── Etapa1_ModeloER/           ← diagrama ER + decisões
│   ├── Etapa2_Relacional/         ← esquema relacional + normalização
│   ├── Etapa3_SQL/                ← DDL + scripts de carga
│   └── Etapa4_EDA/                ← consultas + gráficos
└── Aprendizado/                   ← contexto gerado com IA
```

## Rota de 16 Passos

| # | Passo | Status |
|---|-------|--------|
| 1 | Escolher e validar dataset | ✅ Concluído |
| 2 | Explorar e preparar os dados (Pandas/Jupyter) | ✅ Concluído |
| 3 | Entender colunas e domínio | ✅ Concluído |
| 4 | Identificar entidades e relacionamentos | ✅ Concluído |
| 5 | Definir regras de integridade | ✅ Concluído |
| 6 | Criar diagrama ER/EER | ✅ Concluído |
| 7 | Converter ER para modelo relacional | ✅ Concluído |
| 8 | Normalizar o esquema | ✅ Concluído |
| 9 | Implementar fisicamente o banco (DDL SQL) | ✅ Concluído |
| 10 | Criar pipeline de carga (Python) | ✅ Concluído |
| 11 | Validar a carga | ✅ Concluído |
| 12 | Formular perguntas investigativas | ✅ Concluído |
| 13 | Criar consultas SQL | ✅ Concluído |
| 14 | Produzir visualizações e EDA | ✅ Concluído |
| 15 | Documentar o projeto | ✅ Concluído |
| 16 | Preparar apresentação | ✅ Concluído |

## Decisões Tomadas

- **Dataset substituído:** brasileirao.csv descartado (outro grupo já usava). Novo dataset: Oscar AMPAS.
- **birthplace como texto livre:** cidade/estado/país misturados sem padrão — fica como varchar.
- **CATEGORIA como tabela própria:** 5 valores fixos, garante integridade referencial.
- **religion e orient_sexual nullable:** ausência estrutural, não erro.
- **"Na" em orient_sexual:** string tratada como NULL na carga.
- **PREMIO como entidade central:** cada linha do CSV é um prêmio entregue.
