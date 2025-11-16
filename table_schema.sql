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



create table public.fet_portfolio_holdings (
    id bigserial primary key,
    user_id int not null,
    type varchar(50) not null,          -- Stock, Mutual Fund, Gold
    asset varchar not null,             -- Reliance, HDFC MF, etc.
    symbol varchar(50),                 -- RELIANCE.NS (nullable for MF/Gold)
    quantity numeric not null,          -- units / shares / grams
    average_price numeric not null,     -- avg NAV or avg buy price
    average_nav numeric,
    last_updated_date date not null default current_date
);


create table public.fet_portfolio_holdings_mf_transactions (
    id bigserial primary key,
    user_id int not null,
    fund_name text not null,
    symbol varchar(50),
    txn_date date not null,
    txn_type text check (txn_type in ('Buy','Sell')) not null,
    amount numeric not null,
    nav numeric not null,
    units numeric not null,
    created_at timestamp default now()
);




--------------------------------------- new ------------------------------------------------------
create table fetquest_oneview_users (
  id uuid primary key references auth.users(id) on delete cascade,
  username text not null,
  email text not null unique,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);


create table fetquest_oneview_portfolio_holdings (
    id bigserial primary key,
    user_id uuid not null references auth.users(id) on delete cascade,
    type varchar(50) not null check (type in ('Stock', 'Mutual Fund', 'Gold')),
    asset text not null,                       -- Reliance, HDFC MF, Gold ETF, etc.
    symbol varchar(50),                        -- RELIANCE.NS, MF ISIN, etc.
    quantity numeric(18,6) not null,           -- units / shares / grams
    average_price numeric(18,6) not null,      -- buy price or NAV
    average_nav numeric(18,6),
    last_updated_date date not null default current_date,
    created_at timestamptz default now() not null
);

create table fetquest_oneview_mf_transactions (
    id bigserial primary key,
    user_id uuid not null references auth.users(id) on delete cascade,
    fund_name text not null,
    symbol varchar(50) not null,               -- ISIN or unique MF symbol
    type text not null,
    txn_date date not null,
    txn_type text not null check (txn_type in ('Buy', 'Sell')),
    amount numeric(18,6) not null,             -- invested/redeemed amount
    nav numeric(18,6) not null,
    units numeric(18,6) not null,
    created_at timestamptz default now() not null
);


create index idx_portfolio_user on fetquest_oneview_portfolio_holdings(user_id);
create index idx_mf_txn_user_date on fetquest_oneview_mf_transactions(user_id, txn_date);
create index idx_mf_txn_symbol on fetquest_oneview_mf_transactions(symbol);

alter table fetquest_oneview_users
add column security_question TEXT NOT NULL DEFAULT 'quest';

alter table fetquest_oneview_users
add column security_ANSWER TEXT NOT NULL DEFAULT 'anser';

drop table fetquest_oneview_users;
