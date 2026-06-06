CREATE OR REPLACE VIEW gold.emission_factors_vw AS
SELECT
    r.country_name,
    s.sector_name,
    y.year,
    f.emission_factor_name,
    f.co2e_unit,
    f.activity_unit,
    AVG(f.co2e)                        AS avg_co2e,
    MIN(f.co2e)                        AS min_co2e,
    MAX(f.co2e)                        AS max_co2e,
    AVG(f.co2e / f.activity_value)     AS avg_factor,
    COUNT(*)                           AS record_count
FROM gold.emission_factors f
JOIN gold.region_dim r ON f.region_dim_id = r.region_dim_id
JOIN gold.sector_dim s ON f.sector_dim_id = s.sector_dim_id
JOIN gold.year_dim y   ON f.year_dim_id   = y.year_dim_id
GROUP BY r.country_name, s.sector_name, y.year, f.emission_factor_name, f.co2e_unit, f.activity_unit;
