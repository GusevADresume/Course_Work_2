
create table if not exists candidates(id serial primary key not null, vk_user_id integer, vk_user_first_name varchar(40), vk_user_last_name varchar(50));
create table if not exists whitelist (id serial primary key, candidate_id integer not null references candidates (id), vk_user_id integer);
create table if not exists blacklist (id serial primary key, candidate_id integer not null references candidates (id), vk_user_id integer);