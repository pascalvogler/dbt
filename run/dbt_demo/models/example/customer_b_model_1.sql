
  
    

    create or replace table `key-hope-278006`.`customer_b`.`my_new_table_name`
    
    
    OPTIONS()
    as (
      

with source_data as (

    select 1 as id
    union all
    select null as id

)

select *
from source_data
    );
  