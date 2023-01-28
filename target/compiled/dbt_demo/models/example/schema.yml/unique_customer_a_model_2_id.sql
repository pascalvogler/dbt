
    
    

with dbt_test__target as (

  select id as unique_field
  from `key-hope-278006`.`dev_eu_customer_a`.`customer_a_model_2`
  where id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


