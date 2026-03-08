CREATE TABLE users (
    tg_id      INTEGER UNIQUE
                       NOT NULL,
    username,
    name       TEXT    NOT NULL,
    age        INTEGER NOT NULL,
    nik_pubg   TEXT    NOT NULL,
    id_pubg    INTEGER NOT NULL,
    nik        TEXT,
    rang       INTEGER NOT NULL
                       DEFAULT (0),
    last_date,
    date_vhod          DEFAULT Неизвестно,
    mess_count INTEGER DEFAULT (0) 
)


CREATE TABLE bans (
    tg_id      INTEGER UNIQUE
                       NOT NULL,
    id_pubg    INTEGER NOT NULL
                       UNIQUE,
    message_id,
    prichina,
    date,
    user_men,
    moder_men
)



CREATE TABLE black_list (
    user_id  UNIQUE,
    rison    DEFAULT неизвестна
);

CREATE TABLE bookmarks (
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

CREATE TABLE default_periods (
    command TEXT,
    period  TEXT,
    chat    INTEGER,
    PRIMARY KEY (
        command,
        chat
    )
);

CREATE TABLE dk (
    comand TEXT    PRIMARY KEY,
    dk     INTEGER
);

CREATE TABLE muts (
    user_id,
    rang_moder,
    moder_id,
    moder_men,
    date,
    comments
);


CREATE TABLE perevod (
    self_id  UNIQUE,
    user_id,
    mess_id,
    stavka
);

CREATE TABLE pravils (
    chat_id INTEGER UNIQUE,
    text    TEXT
);

CREATE TABLE texts (
    text_name,
    text
);

CREATE TABLE recommendation (
    user_id,
    pubg_id,
    moder,
    comments,
    rang,
    date,
    recom_id
);

CREATE TABLE warns (
    user_id  INTEGER PRIMARY KEY
                         UNIQUE
                         NOT NULL,
    reason   TEXT,
    moder_id INTEGER,
    date     TEXT,

);

CREATE TABLE warn_snat (
    user_id,
    warn_text,
    moder_give,
    moder_snat
);


CREATE TABLE links (
    link_text      TEXT,
    activate_count INTEGER,
    sost           INTEGER
);

CREATE TABLE stavki (
    user_id    UNIQUE,
    mess_id,
    stavka,
    last_date
);

CREATE TABLE ruletka (
    user_id   INTEGER PRIMARY KEY,
    last_date TEXT
);

CREATE TABLE farma (
    user_id   INTEGER PRIMARY KEY
                         UNIQUE
                         NOT NULL,
    meshok    INTEGER DEFAULT (0),
    last_date TEXT
);

