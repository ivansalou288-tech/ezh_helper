CREATE TABLE IF NOT EXISTS bans (
    tg_id      INTEGER UNIQUE
                       NOT NULL,
    id_pubg    INTEGER NOT NULL
                       UNIQUE,
    message_id INTEGER,
    prichina   TEXT,
    date       TEXT,
    user_men   TEXT,
    moder_men  TEXT
);

CREATE TABLE IF NOT EXISTS black_list (
    user_id INTEGER UNIQUE,
    rison   TEXT    DEFAULT 'неизвестна'
);

CREATE TABLE IF NOT EXISTS bookmarks (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER   NOT NULL,
    chat_id      INTEGER   NOT NULL,
    message_id   INTEGER   NOT NULL,
    message_text TEXT,
    author_id    INTEGER,
    author_name  TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (
        user_id,
        chat_id,
        message_id
    )
);

CREATE TABLE IF NOT EXISTS default_periods (
    command TEXT,
    period  TEXT,
    chat    INTEGER,
    PRIMARY KEY (
        command,
        chat
    )
);

CREATE TABLE IF NOT EXISTS din_admn_user_data (
    user_id,
    pubg_id,
    moder,
    comments,
    rang,
    date
);

CREATE TABLE IF NOT EXISTS dinamic_admn_recommend (
    user_id  UNIQUE,
    is_do
);

CREATE TABLE IF NOT EXISTS dk (
    comand TEXT    PRIMARY KEY,
    dk     INTEGER
);

CREATE TABLE IF NOT EXISTS muts (
    user_id    INTEGER,
    rang_moder INTEGER,
    moder_id   INTEGER,
    moder_men  TEXT,
    date       TEXT,
    comments   TEXT
);

CREATE TABLE IF NOT EXISTS recommendation (
    user_id  INTEGER,
    pubg_id  INTEGER,
    moder    TEXT,
    comments TEXT,
    rang     INTEGER,
    date     TEXT,
    recom_id INTEGER
);

CREATE TABLE IF NOT EXISTS ruletka (
    user_id   INTEGER PRIMARY KEY,
    last_date TEXT
);

CREATE TABLE IF NOT EXISTS stavki (
    user_id   INTEGER UNIQUE,
    mess_id   INTEGER,
    stavka    TEXT,
    last_date TEXT
);

CREATE TABLE IF NOT EXISTS texts (
    text_name TEXT PRIMARY KEY,
    text      TEXT
);

CREATE TABLE IF NOT EXISTS users (
    tg_id      INTEGER UNIQUE
                       NOT NULL,
    username   TEXT,
    name       TEXT    NOT NULL,
    age        INTEGER NOT NULL,
    nik_pubg   TEXT    NOT NULL,
    id_pubg    INTEGER NOT NULL,
    nik        TEXT,
    rang       INTEGER NOT NULL
                       DEFAULT 0,
    last_date  TEXT,
    date_vhod  TEXT    DEFAULT 'Неизвестно',
    mess_count INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS warn_snat (
    user_id    INTEGER,
    warn_text  TEXT,
    moder_give TEXT,
    moder_snat TEXT
);

CREATE TABLE IF NOT EXISTS warns (
    user_id  INTEGER NOT NULL,
    reason   TEXT,
    moder_id INTEGER,
    date     TEXT
);
