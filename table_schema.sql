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
  id bigint not null,
  type character varying(50) not null,
  quantity integer not null,
  average_price double precision not null,
  asset character varying PRIMARY KEY not null,
  symbol character varying(50) not null
) TABLESPACE pg_default;