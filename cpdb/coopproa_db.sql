CREATE DATABASE coopproa_db;
USE coopproa_db;
-- 1. PROVEEDORES
CREATE TABLE proveedores (
  id_prov INT AUTO_INCREMENT PRIMARY KEY,
  nombre_prov VARCHAR(40) NOT NULL,
  contacto VARCHAR(100)
);
 -- 2. PRODUCTOS
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
