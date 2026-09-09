select * from pagos_a_proveedores;
select * from historial_ventas;
select * from productos;
select * from proveedores;
select id_prov from proveedores;

insert into proveedores (nombre_prov, contacto) values('Distribuidora Alimentos S.A.','3512078585');
insert into proveedores (nombre_prov, contacto) values('TecnoWorld Alimentos S.A.','3512078585');
insert into historial_ventas (nombre_prod, cantidad, total, fecha) values('Chupetin_de_fresa', 4, 4000.0, default);
insert into historial_ventas (nombre_prod, cantidad, total, fecha) values('Chesitos', 1, 800.0, default);
insert into productos (nombre_prod, precio_costo, porcentaje_ganancia, precio_venta, stock_actual) values('Chupetin_de_fresa', 800.0, 25.0, 1000.0, 0);
insert into productos (nombre_prod, precio_costo, porcentaje_ganancia, precio_venta, stock_actual) values('Chesitos', 640.0, 1.25, 800.0,0);
insert into pagos_a_proveedores (id_prov, id_prod, cantidad, precio_pago) values(1, 2, 4, 640.0);





alter table pagos_a_proveedores rename column id_prov to nombre_prov;
alter table pagos_a_proveedores modify column nombre_prov VARCHAR(40) NOT NULL;
delete from productos where id_prod = 2;