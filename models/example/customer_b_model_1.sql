{{ config(
    materialized='table',
    alias='my_new_table_name',
    schema='customer_b',
    tags=['b']
) }}

with source_data as (

    select 1 as id
    union all
    select null as id

)

select *
from source_data