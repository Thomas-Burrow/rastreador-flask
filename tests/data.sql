INSERT INTO user (username, password, cargo)
VALUES
  ('test', 'scrypt:32768:8:1$v9tXcUgI6KEd1rjC$368456908b2d1e661d64a6d49b11a5d411ef46a7d7ac01e21012adb6809a03551e93303bf039516c984138aa7cd75b6d34c73a73ba8f90375bd3236e54613e26', 'Gerente'),
  ('other', 'scrypt:32768:8:1$v9tXcUgI6KEd1rjC$368456908b2d1e661d64a6d49b11a5d411ef46a7d7ac01e21012adb6809a03551e93303bf039516c984138aa7cd75b6d34c73a73ba8f90375bd3236e54613e26', 'Usuario');

INSERT INTO ordem_servico (placa, estado, retirado_em)
VALUES
  ('AAA-1234', 'Retirado', '2025-11-12T14:44:21.745360'),
  ('AAA-1234', 'Teste', NULL),
  ('XYZ12C4', 'Oficina', NULL);