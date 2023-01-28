{{ config(
    materialized='view',
    schema='customer_b',
    tags=['b']
) }}

select *
from {{ ref('customer_b_model_1') }}
where id = 1
