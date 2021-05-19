CREATE TABLE public.sku (
	id int4 NOT NULL,
	description text NULL,
	CONSTRAINT sku_pkey PRIMARY KEY (id)
);

CREATE TABLE public.price (
	id int4 NULL,
	price int4 NULL,
	load_date date NULL,
	CONSTRAINT price_id_fkey FOREIGN KEY (id) REFERENCES sku(id) ON DELETE CASCADE
);

CREATE TABLE public.table_updates (
	update_id text NOT NULL,
	target_table text NULL,
	inserted timestamp NULL DEFAULT now(),
	CONSTRAINT table_updates_pkey PRIMARY KEY (update_id)
);

CREATE TABLE public.tmp (
	id int4 NULL,
	description text NULL,
	price int4 NULL,
	load_date date NULL
);