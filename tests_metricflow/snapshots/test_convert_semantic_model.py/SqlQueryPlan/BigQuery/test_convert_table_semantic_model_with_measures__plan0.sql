test_name: test_convert_table_semantic_model_with_measures
test_filename: test_convert_semantic_model.py
docstring:
  Complete test of table semantic model conversion. This includes the full set of measures/entities/dimensions.

      Measures trigger a primary time dimension validation. Additionally, this includes both categorical and time
      dimension types, which should cover most, if not all, of the table source branches in the target class.
sql_engine: BigQuery
---
-- Read Elements From Semantic Model 'id_verifications'
SELECT
  1 AS identity_verifications
  , DATETIME_TRUNC(id_verifications_src_28000.ds, day) AS ds__day
  , DATETIME_TRUNC(id_verifications_src_28000.ds, isoweek) AS ds__week
  , DATETIME_TRUNC(id_verifications_src_28000.ds, month) AS ds__month
  , DATETIME_TRUNC(id_verifications_src_28000.ds, quarter) AS ds__quarter
  , DATETIME_TRUNC(id_verifications_src_28000.ds, year) AS ds__year
  , EXTRACT(year FROM id_verifications_src_28000.ds) AS ds__extract_year
  , EXTRACT(quarter FROM id_verifications_src_28000.ds) AS ds__extract_quarter
  , EXTRACT(month FROM id_verifications_src_28000.ds) AS ds__extract_month
  , EXTRACT(day FROM id_verifications_src_28000.ds) AS ds__extract_day
  , IF(EXTRACT(dayofweek FROM id_verifications_src_28000.ds) = 1, 7, EXTRACT(dayofweek FROM id_verifications_src_28000.ds) - 1) AS ds__extract_dow
  , EXTRACT(dayofyear FROM id_verifications_src_28000.ds) AS ds__extract_doy
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, day) AS ds_partitioned__day
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, isoweek) AS ds_partitioned__week
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, month) AS ds_partitioned__month
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, quarter) AS ds_partitioned__quarter
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, year) AS ds_partitioned__year
  , EXTRACT(year FROM id_verifications_src_28000.ds_partitioned) AS ds_partitioned__extract_year
  , EXTRACT(quarter FROM id_verifications_src_28000.ds_partitioned) AS ds_partitioned__extract_quarter
  , EXTRACT(month FROM id_verifications_src_28000.ds_partitioned) AS ds_partitioned__extract_month
  , EXTRACT(day FROM id_verifications_src_28000.ds_partitioned) AS ds_partitioned__extract_day
  , IF(EXTRACT(dayofweek FROM id_verifications_src_28000.ds_partitioned) = 1, 7, EXTRACT(dayofweek FROM id_verifications_src_28000.ds_partitioned) - 1) AS ds_partitioned__extract_dow
  , EXTRACT(dayofyear FROM id_verifications_src_28000.ds_partitioned) AS ds_partitioned__extract_doy
  , id_verifications_src_28000.verification_type
  , DATETIME_TRUNC(id_verifications_src_28000.ds, day) AS verification__ds__day
  , DATETIME_TRUNC(id_verifications_src_28000.ds, isoweek) AS verification__ds__week
  , DATETIME_TRUNC(id_verifications_src_28000.ds, month) AS verification__ds__month
  , DATETIME_TRUNC(id_verifications_src_28000.ds, quarter) AS verification__ds__quarter
  , DATETIME_TRUNC(id_verifications_src_28000.ds, year) AS verification__ds__year
  , EXTRACT(year FROM id_verifications_src_28000.ds) AS verification__ds__extract_year
  , EXTRACT(quarter FROM id_verifications_src_28000.ds) AS verification__ds__extract_quarter
  , EXTRACT(month FROM id_verifications_src_28000.ds) AS verification__ds__extract_month
  , EXTRACT(day FROM id_verifications_src_28000.ds) AS verification__ds__extract_day
  , IF(EXTRACT(dayofweek FROM id_verifications_src_28000.ds) = 1, 7, EXTRACT(dayofweek FROM id_verifications_src_28000.ds) - 1) AS verification__ds__extract_dow
  , EXTRACT(dayofyear FROM id_verifications_src_28000.ds) AS verification__ds__extract_doy
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, day) AS verification__ds_partitioned__day
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, isoweek) AS verification__ds_partitioned__week
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, month) AS verification__ds_partitioned__month
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, quarter) AS verification__ds_partitioned__quarter
  , DATETIME_TRUNC(id_verifications_src_28000.ds_partitioned, year) AS verification__ds_partitioned__year
  , EXTRACT(year FROM id_verifications_src_28000.ds_partitioned) AS verification__ds_partitioned__extract_year
  , EXTRACT(quarter FROM id_verifications_src_28000.ds_partitioned) AS verification__ds_partitioned__extract_quarter
  , EXTRACT(month FROM id_verifications_src_28000.ds_partitioned) AS verification__ds_partitioned__extract_month
  , EXTRACT(day FROM id_verifications_src_28000.ds_partitioned) AS verification__ds_partitioned__extract_day
  , IF(EXTRACT(dayofweek FROM id_verifications_src_28000.ds_partitioned) = 1, 7, EXTRACT(dayofweek FROM id_verifications_src_28000.ds_partitioned) - 1) AS verification__ds_partitioned__extract_dow
  , EXTRACT(dayofyear FROM id_verifications_src_28000.ds_partitioned) AS verification__ds_partitioned__extract_doy
  , id_verifications_src_28000.verification_type AS verification__verification_type
  , id_verifications_src_28000.verification_id AS verification
  , id_verifications_src_28000.user_id AS user
  , id_verifications_src_28000.user_id AS verification__user
FROM ***************************.fct_id_verifications id_verifications_src_28000
