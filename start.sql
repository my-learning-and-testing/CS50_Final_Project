/*
    бд пользователей
    id      имя_пользователя    хеш_пароля      дата_первого_входа     дата_последнего_входа

    бд документов
    id      id_пользователя     документ        дата_окончания         время_на_перевыпуск     ограничено_действ_время

    бд отзывов
    id      id_пользователя     текст    дата
*/

    CREATE TABLE users (
        id INTEGER NOT NULL,
  username TEXT NOT NULL UNIQUE,
      hash TEXT NOT NULL,
firstentry DATETIME NOT NULL,
 lastentry DATETIME NOT NULL,
   PRIMARY KEY(id)
);

CREATE TABLE goods (
        id INTEGER NOT NULL,
  users_id INTEGER NOT NULL,
      icon INTEGER NOT NULL DEFAULT 0
 goodsname TEXT NOT NULL,
   enddate DATETIME NOT NULL,
 lastdays1 INTEGER NOT NULL DEFAULT 0,
 lastdays2 INTEGER NOT NULL DEFAULT 0,
   FOREIGN KEY(users_id) REFERENCES users(id),
   PRIMARY KEY(id)
);

CREATE TABLE feedback (
        id INTEGER NOT NULL,
  users_id INTEGER NOT NULL,
      text TEXT NOT NULL,
      date DATETIME NOT NULL,
   FOREIGN KEY(users_id) REFERENCES users(id),
   PRIMARY KEY(id)
);
