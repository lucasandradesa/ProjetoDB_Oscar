-- =============================================================
-- Passo 11 — Validação da Carga
-- Oscar AMPAS — Disciplina: Banco de Dados — DCC/UFMG
-- =============================================================

-- -------------------------------------------------------------
-- 1. Contagem por tabela
-- -------------------------------------------------------------
SELECT 'edicao'    AS tabela, COUNT(*) AS total FROM edicao    UNION ALL
SELECT 'categoria',            COUNT(*)          FROM categoria UNION ALL
SELECT 'filme',                COUNT(*)          FROM filme     UNION ALL
SELECT 'vencedor',             COUNT(*)          FROM vencedor  UNION ALL
SELECT 'premio',               COUNT(*)          FROM premio
ORDER BY tabela;

-- -------------------------------------------------------------
-- 2. Integridade referencial — prêmios sem vencedor, filme, etc.
-- -------------------------------------------------------------
SELECT 'premios sem vencedor'  AS check, COUNT(*) FROM premio WHERE id_vencedor  NOT IN (SELECT id_vencedor  FROM vencedor)  UNION ALL
SELECT 'premios sem filme',              COUNT(*) FROM premio WHERE id_filme      NOT IN (SELECT id_filme      FROM filme)      UNION ALL
SELECT 'premios sem categoria',          COUNT(*) FROM premio WHERE id_categoria  NOT IN (SELECT id_categoria  FROM categoria)  UNION ALL
SELECT 'premios sem edicao',             COUNT(*) FROM premio WHERE id_edicao     NOT IN (SELECT id_edicao     FROM edicao);

-- -------------------------------------------------------------
-- 3. Unicidade — ninguém ganha a mesma categoria na mesma edição duas vezes
-- -------------------------------------------------------------
SELECT id_vencedor, id_categoria, id_edicao, COUNT(*) AS ocorrencias
FROM premio
GROUP BY id_vencedor, id_categoria, id_edicao
HAVING COUNT(*) > 1;

-- -------------------------------------------------------------
-- 4. NULLs esperados — religião e orientação sexual
-- -------------------------------------------------------------
SELECT
    COUNT(*)                                    AS total_vencedores,
    COUNT(*) FILTER (WHERE religiao IS NULL)    AS religiao_nula,
    COUNT(*) FILTER (WHERE orient_sexual IS NULL) AS orient_nula
FROM vencedor;

-- -------------------------------------------------------------
-- 5. Vencedores com mais de um Oscar
-- -------------------------------------------------------------
SELECT v.nome, COUNT(*) AS total_oscars
FROM premio p
JOIN vencedor v ON v.id_vencedor = p.id_vencedor
GROUP BY v.nome
HAVING COUNT(*) > 1
ORDER BY total_oscars DESC;

-- -------------------------------------------------------------
-- 6. Categorias presentes — devem ser exatamente 5
-- -------------------------------------------------------------
SELECT nome, COUNT(*) AS vezes_entregue
FROM categoria c
JOIN premio p ON p.id_categoria = c.id_categoria
GROUP BY nome
ORDER BY vezes_entregue DESC;

-- -------------------------------------------------------------
-- 7. Distribuição de vencedores por etnia
-- -------------------------------------------------------------
SELECT etnia, COUNT(*) AS total
FROM vencedor
GROUP BY etnia
ORDER BY total DESC;

-- -------------------------------------------------------------
-- 8. Edições com número de prêmios diferente de 5
-- -------------------------------------------------------------
SELECT e.ano, COUNT(*) AS premios_na_edicao
FROM edicao e
JOIN premio p ON p.id_edicao = e.id_edicao
GROUP BY e.ano
HAVING COUNT(*) <> 5
ORDER BY e.ano;
