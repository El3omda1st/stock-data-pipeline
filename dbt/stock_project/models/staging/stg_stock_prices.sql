with raw_data as (
    select
        date::date as date,
        ticker as company,
        open::float as open,
        high::float as high,
        low::float as low,
        close::float as close,
        volume::bigint as volume
    from {{ source('finance', 'stock_prices') }}
)

select * from raw_data