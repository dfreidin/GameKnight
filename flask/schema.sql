CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL
    -- add more login stuff
);

CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    bgg_id INT UNIQUE NOT NULL
);
CREATE INDEX ON games (name);
CREATE INDEX ON games (bgg_id);

CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id INT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    rating INT,
    owned BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ON ratings (user_id);
CREATE INDEX ON ratings (game_id);

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
CREATE INDEX ON groups (name);

CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ON members (user_id);
CREATE INDEX ON members (group_id);

CREATE TABLE IF NOT EXISTS friends (
    id SERIAL PRIMARY KEY,
    instigator_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    requested_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    accepted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ON friends (instigator_id);
CREATE INDEX ON friends (requested_id);