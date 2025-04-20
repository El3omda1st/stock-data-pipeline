with data as (
    select
    date,
    company,
    open,
    high,
    low,
    close,
    volume
from {{ ref('stg_stock_prices') }}
)
select * from data