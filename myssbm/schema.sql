drop table if exists users;
create table users (
  tag text primary key not null,
  password text not null,
  main text,
  email text not null
);

drop table if exists sets;
create table sets (
  set_id integer primary key autoincrement,
  tag_1 text not null,
  tag_2 text not null,
  wins_1 integer not null,
  wins_2 integer not null,
  char_1 text,
  char_2 text,
  tournament text,
  FOREIGN KEY(tournament) REFERENCES tournaments(tourn_name)

);

drop table if exists tournaments;
create table tournaments (
  tourney_id integer primary key autoincrement,
  tourn_name text not null
);

drop table if exists placings;
create table placings (
  placing_id integer primary key autoincrement,
  placing integer not null,
  tag text not null,
  tournament text not null,
  FOREIGN KEY(tag) REFERENCES users(tag),
  FOREIGN KEY(tournament) REFERENCES tournaments(tourn_name)
);
