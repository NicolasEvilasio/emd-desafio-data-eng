-- Define os CTEs
WITH source AS (
    SELECT
        *
    FROM
        {{source ('bronze', 'brt_data')}}
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
	b.codigo,
	DATE(TO_TIMESTAMP(b."dataHora" / 1000) AT TIME ZONE 'UTC' AT TIME ZONE '-03:00') AS "data",
	TO_CHAR(TO_TIMESTAMP(b."dataHora" / 1000) AT TIME ZONE 'UTC' AT TIME ZONE '-03:00', 'HH24:MI:SS') AS "hora",
	b.latitude,
	b.longitude,
	b.velocidade
FROM
	source b
JOIN
	last_info l ON b.codigo = l.codigo AND b."dataHora" = l.max_data
ORDER BY
    codigo,
	"data" DESC,
	hora DESC
