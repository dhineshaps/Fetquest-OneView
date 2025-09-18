CREATE TABLE public.fet_portfolio (
username VARCHAR (50) NOT NULL,
asset VARCHAR (50) NOT NULL,
quantity INT NOT NULL,
average_price INT NOT NULL
 );


 CREATE TABLE public.fet_portfolio_users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);



-- create table public.fet_portfolio_holdings (
--   id bigint not null,
--   type character varying(50) not null,
--   quantity integer not null,
--   average_price double precision not null,
--   asset character varying PRIMARY KEY not null,
--   symbol character varying(50) not null
-- ) TABLESPACE pg_default;



create table public.fet_portfolio_holdings (
    id bigserial primary key,
    user_id int not null,
    type varchar(50) not null,          -- Stock, Mutual Fund, Gold
    asset varchar not null,             -- Reliance, HDFC MF, etc.
    symbol varchar(50),                 -- RELIANCE.NS (nullable for MF/Gold)
    quantity numeric not null,          -- units / shares / grams
    average_price numeric not null,     -- avg NAV or avg buy price
    last_updated_date date not null default current_date
);


create table public.fet_portfolio_holdings_mf_transactions (
    id bigserial primary key,
    user_id int not null,
    fund_name text not null,
    txn_date date not null,
    txn_type text check (txn_type in ('Buy','Sell')) not null,
    amount numeric not null,
    nav numeric not null,
    units numeric not null,
    created_at timestamp default now()
);