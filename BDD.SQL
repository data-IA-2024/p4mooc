-- init module vector
CREATE EXTENSION vector;

CREATE TABLE public.documents (
	id bigserial NOT NULL,
	"text" varchar(2000) NULL,
	embedding public.vector(768) NULL,
	CONSTRAINT documents_pkey PRIMARY KEY (id)
);