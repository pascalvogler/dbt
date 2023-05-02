
  
    

    create or replace table `key-hope-278006`.`customer_a`.`my_new_table_name`
    
    
    OPTIONS()
    as (
      

with source_data as (

    select 2 as id
    union all
    select null as id

)

select *
from source_data
    );
  