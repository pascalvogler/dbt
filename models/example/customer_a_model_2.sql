{{ config(
    materialized='view',
    schema='customer_a',
    tags=['a']
) }}


select *
from {{ ref('customer_a_model_1') }}
where id = 1
