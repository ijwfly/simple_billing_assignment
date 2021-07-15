CREATE SCHEMA billing;

CREATE TYPE billing.transaction_status AS ENUM ('registered', 'completed', 'declined', 'error');
CREATE TYPE billing.direction AS ENUM('credit', 'debit');

CREATE TABLE billing.transaction
(
    id bigserial PRIMARY KEY,
    operation_id text NOT NULL,
    wallet_id bigint NOT NULL,
    status billing.transaction_status NOT NULL DEFAULT 'registered',
    direction billing.direction NOT NULL,
    amount bigint NOT NULL DEFAULT 0,
    cdate timestamp WITH TIME ZONE NOT NULL default NOW(),
    response_code integer
);

CREATE INDEX wallet_id_idx ON billing.transaction using hash(wallet_id);
CREATE INDEX operation_id_idx ON billing.transaction using hash(operation_id);
CREATE INDEX cdate_idx ON billing.transaction using btree(cdate);

CREATE TABLE billing.wallet
(
    id bigserial PRIMARY KEY,
    balance bigint NOT NULL DEFAULT 0,
    user_id bigint NOT NULL
);

CREATE UNIQUE INDEX user_id_idx ON billing.wallet USING btree(user_id);
