CREATE DATABASE IF NOT EXISTS coopproa_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE coopproa_db;

-- Esquema inicial para instalación nueva. No borra tablas ni datos existentes.
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proveedores (
  id_prov INT AUTO_INCREMENT PRIMARY KEY,
  nombre_prov VARCHAR(100) NOT NULL,
  contacto VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS productos (
  id_prod INT AUTO_INCREMENT PRIMARY KEY,
  nombre_prod VARCHAR(100) NOT NULL,
  categoria VARCHAR(40) NOT NULL DEFAULT 'General',
  precio_costo DECIMAL(10,2) NOT NULL DEFAULT 0,
  porcentaje_ganancia DECIMAL(6,2) NOT NULL DEFAULT 0,
  precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock_actual INT UNSIGNED NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pagos_a_proveedores (
  id_pagoprove INT AUTO_INCREMENT PRIMARY KEY,
  id_prov INT NOT NULL,
  id_prod INT NOT NULL,
  id_usuario INT NOT NULL,
  cantidad INT UNSIGNED NOT NULL,
  precio_pago DECIMAL(10,2) NOT NULL,
  fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_pagos_proveedor (id_prov),
  INDEX idx_pagos_producto (id_prod),
  INDEX idx_pagos_usuario (id_usuario),
  CONSTRAINT fk_pagos_proveedor FOREIGN KEY (id_prov)
    REFERENCES proveedores(id_prov) ON DELETE RESTRICT,
  CONSTRAINT fk_pagos_producto FOREIGN KEY (id_prod)
    REFERENCES productos(id_prod) ON DELETE RESTRICT,
  CONSTRAINT fk_pagos_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS historial_ventas (
  id_venta INT AUTO_INCREMENT PRIMARY KEY,
  id_usuario INT NOT NULL,
  id_prod INT NOT NULL,
  cantidad INT UNSIGNED NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ventas_fecha (fecha),
  INDEX idx_ventas_producto (id_prod),
  INDEX idx_ventas_usuario (id_usuario),
  CONSTRAINT fk_ventas_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
  CONSTRAINT fk_ventas_producto FOREIGN KEY (id_prod)
    REFERENCES productos(id_prod) ON DELETE RESTRICT
);
