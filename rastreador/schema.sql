DROP TABLE IF EXISTS user, ordem_servico, logs;

CREATE TABLE user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  cargo TEXT NOT NULL DEFAULT "Usuario"
);

CREATE TABLE ordem_servico (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  placa TEXT NOT NULL,
  estado TEXT NOT NULL,
  retirado_em TIMESTAMP
);

CREATE TABLE logs (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  ordem_servico_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  acao TEXT NOT NULL,
  payload TEXT,
  quando TIMESTAMP
);