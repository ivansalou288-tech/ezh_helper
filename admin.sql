CREATE TABLE IF NOT EXISTS admins (
    user_id,
    chat_id,
    chat_name,
    can_see_users,
    can_do_admin,
    can_recom,
    can_links,
    can_dk
);

CREATE TABLE IF NOT EXISTS creators (
    user_id,
    chat_id
);
