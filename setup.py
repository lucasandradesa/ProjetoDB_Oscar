"""
Setup do banco — Oscar AMPAS
Executa uma única vez após subir o container com:  docker compose up -d

  python setup.py

Pré-requisitos:
  - Docker Desktop instalado e rodando
  - Python 3 com pip
"""

import sys
import subprocess
import time

# ── Instala dependências ──────────────────────────────────────────────
subprocess.check_call([sys.executable, "-m", "pip", "install",
                       "psycopg2-binary", "pandas", "-q"])

import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from pathlib import Path

# ── Caminhos ─────────────────────────────────────────────────────────
ROOT    = Path(__file__).parent
DDL     = ROOT / "Documentacao" / "Etapa3_SQL" / "01_ddl_criar_tabelas.sql"
CSV     = ROOT / "world_ampas_oscar_winner_demographics.csv"

DB = dict(host="localhost", port=5432, dbname="oscar",
          user="postgres", password="brasil123")

# ── Aguarda o PostgreSQL inicializar ─────────────────────────────────
print("Aguardando PostgreSQL inicializar", end="", flush=True)
for _ in range(30):
    try:
        conn = psycopg2.connect(**DB)
        conn.close()
        print(" OK")
        break
    except psycopg2.OperationalError:
        print(".", end="", flush=True)
        time.sleep(2)
else:
    print("\nERRO: PostgreSQL não respondeu em 60 s.")
    print("Verifique se o container está rodando:  docker compose up -d")
    sys.exit(1)

# ── DDL ──────────────────────────────────────────────────────────────
print("\n[1/2] Criando tabelas...")
conn = psycopg2.connect(**DB)
cur  = conn.cursor()
cur.execute(DDL.read_text(encoding="utf-8"))
conn.commit()
cur.close()
conn.close()
print("      Tabelas criadas.")

# ── Carga ─────────────────────────────────────────────────────────────
print("\n[2/2] Carregando dados...")

def nulo(val):
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val

df = pd.read_csv(CSV)
df["sexual_orientation"] = df["sexual_orientation"].replace("Na", None)
df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")

conn = psycopg2.connect(**DB)
cur  = conn.cursor()

try:
    # edicao
    execute_values(cur,
        "INSERT INTO edicao (ano) VALUES %s ON CONFLICT DO NOTHING",
        [(int(a),) for a in sorted(df["year_edition"].unique())])
    conn.commit()
    cur.execute("SELECT ano, id_edicao FROM edicao")
    edicao_id = {r[0]: r[1] for r in cur.fetchall()}
    print(f"      edicao    : {len(edicao_id)} registros")

    # categoria
    execute_values(cur,
        "INSERT INTO categoria (nome) VALUES %s ON CONFLICT DO NOTHING",
        [(str(c),) for c in df["category"].dropna().unique()])
    conn.commit()
    cur.execute("SELECT nome, id_categoria FROM categoria")
    categoria_id = {r[0]: r[1] for r in cur.fetchall()}
    print(f"      categoria : {len(categoria_id)} registros")

    # filme
    execute_values(cur,
        "INSERT INTO filme (titulo) VALUES %s ON CONFLICT DO NOTHING",
        [(str(f),) for f in df["movie"].dropna().unique()])
    conn.commit()
    cur.execute("SELECT titulo, id_filme FROM filme")
    filme_id = {r[0]: r[1] for r in cur.fetchall()}
    print(f"      filme     : {len(filme_id)} registros")

    # vencedor
    venc = df.drop_duplicates(subset="name")[
        ["name","birth_year","birth_date","birthplace",
         "race_ethnicity","religion","sexual_orientation"]]
    execute_values(cur,
        """INSERT INTO vencedor
           (nome, ano_nascimento, data_nascimento, local_nascimento,
            etnia, religiao, orient_sexual)
           VALUES %s ON CONFLICT DO NOTHING""",
        [(row["name"], nulo(row["birth_year"]), nulo(row["birth_date"]),
          nulo(row["birthplace"]), row["race_ethnicity"],
          nulo(row["religion"]), nulo(row["sexual_orientation"]))
         for _, row in venc.iterrows()])
    conn.commit()
    cur.execute("SELECT nome, id_vencedor FROM vencedor")
    vencedor_id = {r[0]: r[1] for r in cur.fetchall()}
    print(f"      vencedor  : {len(vencedor_id)} registros")

    # premio
    linhas = [(vencedor_id[r["name"]], filme_id[r["movie"]],
               categoria_id[r["category"]], edicao_id[int(r["year_edition"])])
              for _, r in df.iterrows()]
    execute_values(cur,
        "INSERT INTO premio (id_vencedor, id_filme, id_categoria, id_edicao) VALUES %s",
        linhas)
    conn.commit()
    print(f"      premio    : {len(linhas)} registros")

except Exception as e:
    conn.rollback()
    print(f"\nERRO durante a carga: {e}")
    raise
finally:
    cur.close()
    conn.close()

print("\nSetup concluído! Banco oscar pronto para uso.")
