drop database COOKING;
create database COOKING;
use cooking;

INSERT INTO usuarios (correo,nombre,contrasenia) VALUES ('admin@correo.com', 'admin','scrypt:32768:8:1$5eLEnxCeiot2GuHd$8b506093b601d50165a20cfd6a1971afde4d60d1b1e1f72f87d63472c893af4a243a2a3135a90db59ce9b82b1d6636acbe5514d5c4e56a10453d4b75deaaf3a7');

INSERT INTO roles (nombre) VALUES ('admin');
INSERT INTO roles (nombre) VALUES ('vendedor');
INSERT INTO roles (nombre) VALUES ('cocinero');

INSERT INTO asignaciones_rol_usuario(idUsuario, idRol) VALUES (1,1);
INSERT INTO asignaciones_rol_usuario(idUsuario, idRol) VALUES (1,2);
INSERT INTO asignaciones_rol_usuario(idUsuario, idRol) VALUES (1,3);

INSERT INTO lotes_galletas (fecha_entrada, cantidad, merma, tipo_venta, idProduccion, idReceta, idUsuarios)
VALUES ('2023-04-01', 100, 5, 1, 1, 1, 1),
       ('2023-04-02', 200, 10, 2, 2, 1, 1),
       ('2023-04-03', 300, 15, 3, 1, 2, 1),
       ('2023-04-04', 400, 20, 4, 2, 2, 1),
       ('2023-04-05', 500, 25, 5, 1, 2, 1);