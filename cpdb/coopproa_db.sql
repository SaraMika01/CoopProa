CREATE DATABASE coopproa_db;
USE coopproa_db;
-- 1. PROVEEDORES
CREATE TABLE proveedores (
  id_prov INT AUTO_INCREMENT PRIMARY KEY,
  nombre_prov VARCHAR(40) NOT NULL,
  contacto VARCHAR(100)
);
 -- 2. PRODUCTOScompras_a_proveedores
CREATE TABLE productos (
  id_prod INT AUTO_INCREMENT PRIMARY KEY,
  nombre_prod VARCHAR(40) NOT NULL,
  precio_costo DECIMAL(10,2) NOT NULL DEFAULT 0,
  porcentaje_ganancia DECIMAL(10,2) NOT NULL DEFAULT 0,
  precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock_actual INT NOT NULL DEFAULT 0
);
-- 3. COMPRAS QUE VOS HICISTE A PROVEEDORES
CREATE TABLE pagos_a_proveedores (
  id_pagoprove INT AUTO_INCREMENT PRIMARY KEY,
  id_prov INT Not null,
  id_prod INT,
  cantidad INT,
  precio_pago DECIMAL(10,2) NOT NULL,
  fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_prov) REFERENCES proveedores(id_prov),
  FOREIGN KEY (id_prod) REFERENCES productos(id_prod)
);

create table historial_ventas (
nombre_prod VARCHAR(50) NOT NULL,
cantidad int not null,
total DECIMAL NOT NULL,
fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);
select * from pagos_a_proveedores;
select * from historial_ventas;
select * from productos;
select * from proveedores;
select id_prov from proveedores;

insert into proveedores (nombre, contacto) values('Distribuidora Alimentos S.A.','3512078585');
insert into proveedores (nombre, contacto) values('TecnoWorld Alimentos S.A.','3512078585');
insert into proveedores (nombre, contacto) values('Distribuidora Alimentos S.A.', '3512078585');
insert into proveedores (nombre, contacto) values('Distribuidora Alimentos S.A.','3512078585');
insert into proveedores (nombre, contacto) values('Distribuidora Alimentos S.A.','3512078585');

insert into historial_ventas (nom_prod, cantidad, total,precio) values('Chupetin_de_fresa', 4, 400.0, default);
insert into historial_ventas (nom_prod, cantidad, total,precio) values('Chesitos', 1, 800.0, default);
insert into historial_ventas (nom_prod, cantidad, total,precio) values('Chesitos', 1, 800.0, default);
insert into historial_ventas (nom_prod, cantidad, total,precio) values('Chesitos', 1, 800.0, default);
insert into historial_ventas (nom_prod, cantidad, total,precio) values('Chesitos', 1, 800.0, default);

insert into productos (nombre, precio_venta, stock_actual) values('Chupetin_de_fresa', 400.0, 0);
insert into productos (nombre, precio_venta, stock_actual) values('Chesitos', 800.0, 0);
insert into productos (nombre, precio_venta, stock_actual) values('jugo_baggio', 950.0, 0);
insert into productos (nombre, precio_venta, stock_actual) values('caramelo_alka', 800.0, 0);
insert into productos (nombre, precio_venta, stock_actual) values('alfajor_tatin', 700.0, 0);

insert into compras_a_proveedores (proveedor_id, producto_id, cantidad, precio_compra, fecha_compra) values (1, 2, 9, 640.0, '2026-09-10');
insert into compras_a_proveedores (proveedor_id, producto_id, cantidad, precio_compra, fecha_compra) values (3, 2, 4, 610.0,  '2026-09-10');
insert into compras_a_proveedores (proveedor_id, producto_id, cantidad, precio_compra, fecha_compra) values (1, 3, 2, 240.0,  '2026-09-10');
insert into compras_a_proveedores (proveedor_id, producto_id, cantidad, precio_compra, fecha_compra) values (7, 2, 1, 6400.0,  '2026-09-10');
insert into compras_a_proveedores (proveedor_id, producto_id, cantidad, precio_compra, fecha_compra) values (9, 9, 4, 640.0,  '2026-09-10');


alter table pagos_a_proveedores rename column id_prov to nombre_prov;
alter table pagos_a_proveedores modify column nombre_prov VARCHAR(40) NOT NULL;
delete from productos where id_prod = 2;


select * from productos;
select * from historial_ventas;

