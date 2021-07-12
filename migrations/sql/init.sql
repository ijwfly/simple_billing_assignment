CREATE SCHEMA billing;

CREATE TYPE billing.transaction_status AS ENUM ('registered', 'completed', 'declined', 'error');
CREATE TYPE billing.direction AS ENUM('credit', 'debit');

CREATE TABLE billing.transaction
(
    id bigserial PRIMARY KEY,
    wallet_id bigint NOT NULL,
    status billing.transaction_status NOT NULL,
    direction billing.direction NOT NULL,
    amount bigint NOT NULL DEFAULT 0
);

CREATE INDEX wallet_id_idx ON billing.transaction using hash(wallet_id);

CREATE TABLE billing.wallet
(
    id bigserial PRIMARY KEY,
    balance bigint NOT NULL DEFAULT 0,
    user_id bigint NOT NULL
);

CREATE UNIQUE INDEX user_id_idx ON billing.wallet USING btree(user_id);
