DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ordem_servico;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE ordem_servico (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placa TEXT NOT NULL,
  estado TEXT NOT NULL,
  oficina_completa INTEGER NOT NULL DEFAULT 0 CHECK (oficina_completa IN (0,1)),
  teste_completo INTEGER NOT NULL DEFAULT 0 CHECK (teste_completo IN (0,1)),
  lavagem_completa INTEGER NOT NULL DEFAULT 0 CHECK (lavagem_completa IN (0,1)),
  retirado_em TIMESTAMP
);