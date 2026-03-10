CREATE TABLE admin_permissions (
    id              INTEGER   PRIMARY KEY AUTOINCREMENT,
    admin_id        INTEGER,
    chat_id         INTEGER,
    permission_name TEXT,
    granted         BOOLEAN   DEFAULT [FALSE],
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (
        admin_id,
        chat_id
    )
    REFERENCES admins (user_id,
    chat_id) 
);

CREATE TABLE admins (
    user_id    INTEGER,
    chat_id    INTEGER,
    rang       INTEGER   DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (
        user_id,
        chat_id
    )
);

CREATE TABLE all_users (
    user_id   UNIQUE,
    username
);

CREATE TABLE chat_info (
    chat_id        INTEGER   PRIMARY KEY,
    chat_title     TEXT,
    chat_username  TEXT,
    chat_photo_url TEXT,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE farma (
    user_id   UNIQUE,
    meshok    INTEGER,
    last_date
);

CREATE TABLE perevod (
    self_id  UNIQUE,
    user_id,
    mess_id,
    stavka
);

CREATE TABLE stavki (
    user_id    UNIQUE,
    mess_id,
    stavka,
    last_date
);

