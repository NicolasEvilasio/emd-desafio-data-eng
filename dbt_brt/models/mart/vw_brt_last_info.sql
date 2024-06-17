-- Define os CTEs
WITH source AS (
    SELECT
        *
    FROM
        {{source ('public', 'brt_data')}}
),
last_info AS (
	SELECT DISTINCT
		codigo,
		MAX("dataHora") AS max_data
	FROM
	    source
	GROUP BY
		codigo
)
-- Consulta principal
SELECT DISTINCT
	codigo,
	DATE(TO_TIMESTAMP("dataHora" / 1000) AT TIME ZONE 'UTC' AT TIME ZONE '-03:00') AS "data",
	TO_CHAR(TO_TIMESTAMP("dataHora" / 1000) AT TIME ZONE 'UTC' AT TIME ZONE '-03:00', 'HH24:MI:SS') AS "hora",
	latitude,
	longitude,
	velocidade
FROM
	source
WHERE
	codigo IN (SELECT codigo FROM last_info)
	AND "dataHora" IN (SELECT "dataHora" FROM last_info)
ORDER BY
	"data" DESC,
	hora DESC
