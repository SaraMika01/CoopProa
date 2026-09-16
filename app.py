import os
from contextlib import closing
from datetime import date

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__, template_folder="temples", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "coopproa-dev-key")


def conectar_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "12345"),
        database=os.getenv("DB_NAME", "coopproa_db"),
    )


def consultar(sql, parametros=(), uno=False):
    with closing(conectar_db()) as conexion:
        with closing(conexion.cursor(dictionary=True)) as cursor:
            cursor.execute(sql, parametros)
            return cursor.fetchone() if uno else cursor.fetchall()


def ejecutar(sql, parametros=(), varios=False):
    with closing(conectar_db()) as conexion:
        with closing(conexion.cursor()) as cursor:
            if varios:
                cursor.executemany(sql, parametros)
            else:
                cursor.execute(sql, parametros)
            conexion.commit()
            return cursor.lastrowid


def preparar_esquema():
    """Agrega columnas nuevas sin borrar datos de instalaciones existentes."""
    with closing(conectar_db()) as conexion:
        with closing(conexion.cursor()) as cursor:
            cursor.execute("SHOW COLUMNS FROM productos LIKE 'categoria'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(40) NOT NULL DEFAULT 'General'")
            cursor.execute("SHOW COLUMNS FROM historial_ventas LIKE 'id_venta'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE historial_ventas ADD COLUMN id_venta INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST")
            conexion.commit()


@app.route("/")
def inicio():
    resumen = {
        "productos": consultar("SELECT COUNT(*) AS total FROM productos", uno=True)["total"],
        "proveedores": consultar("SELECT COUNT(*) AS total FROM proveedores", uno=True)["total"],
        "ventas_hoy": consultar(
            "SELECT COALESCE(SUM(total), 0) AS total FROM historial_ventas WHERE DATE(fecha) = %s",
            (date.today(),), uno=True
        )["total"],
    }
    return render_template("index.html", resumen=resumen)


@app.route("/inventario", methods=["GET", "POST"])
def inventario():
    if request.method == "POST":
        ejecutar(
            """INSERT INTO productos
               (nombre_prod, categoria, precio_costo, porcentaje_ganancia, precio_venta, stock_actual)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (request.form["nombre_prod"], request.form.get("categoria", "General"),
             request.form.get("precio_costo", 0), request.form.get("porcentaje_ganancia", 0),
             request.form["precio_venta"], request.form.get("stock_actual", 0)),
        )
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("inventario"))
    productos = consultar("SELECT * FROM productos ORDER BY nombre_prod")
    return render_template("inventario.html", productos=productos)


@app.post("/inventario/<int:id_prod>/editar")
def editar_producto(id_prod):
    ejecutar(
        """UPDATE productos SET nombre_prod=%s, categoria=%s, precio_costo=%s,
           porcentaje_ganancia=%s, precio_venta=%s, stock_actual=%s WHERE id_prod=%s""",
        (request.form["nombre_prod"], request.form.get("categoria", "General"),
         request.form.get("precio_costo", 0), request.form.get("porcentaje_ganancia", 0),
         request.form["precio_venta"], request.form.get("stock_actual", 0), id_prod),
    )
    flash("Producto actualizado correctamente.", "success")
    return redirect(url_for("inventario"))


@app.post("/inventario/<int:id_prod>/eliminar")
def eliminar_producto(id_prod):
    ejecutar("DELETE FROM productos WHERE id_prod=%s", (id_prod,))
    flash("Producto eliminado.", "success")
    return redirect(url_for("inventario"))


@app.route("/proveedores", methods=["GET", "POST"])
def proveedores():
    if request.method == "POST":
        ejecutar("INSERT INTO proveedores (nombre_prov, contacto) VALUES (%s, %s)",
                 (request.form["nombre_prov"], request.form.get("contacto", "")))
        flash("Proveedor creado correctamente.", "success")
        return redirect(url_for("proveedores"))
    datos = consultar("""SELECT p.*, COUNT(c.id_pagoprove) AS compras,
                        COALESCE(SUM(c.precio_pago * c.cantidad), 0) AS total_compras
                        FROM proveedores p LEFT JOIN pagos_a_proveedores c ON c.id_prov = p.id_prov
                        GROUP BY p.id_prov ORDER BY p.nombre_prov""")
    return render_template("proveedores.html", proveedores=datos)


@app.post("/proveedores/<int:id_prov>/editar")
def editar_proveedor(id_prov):
    ejecutar("UPDATE proveedores SET nombre_prov=%s, contacto=%s WHERE id_prov=%s",
             (request.form["nombre_prov"], request.form.get("contacto", ""), id_prov))
    flash("Proveedor actualizado correctamente.", "success")
    return redirect(url_for("proveedores"))


@app.post("/proveedores/<int:id_prov>/eliminar")
def eliminar_proveedor(id_prov):
    try:
        ejecutar("DELETE FROM proveedores WHERE id_prov=%s", (id_prov,))
        flash("Proveedor eliminado.", "success")
    except mysql.connector.IntegrityError:
        flash("No se puede eliminar un proveedor con compras asociadas.", "danger")
    return redirect(url_for("proveedores"))


@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    if request.method == "POST":
        producto = consultar("SELECT * FROM productos WHERE id_prod=%s", (request.form["id_prod"],), uno=True)
        cantidad = int(request.form["cantidad"])
        if not producto or producto["stock_actual"] < cantidad:
            flash("No hay stock suficiente para registrar la venta.", "danger")
        else:
            total = producto["precio_venta"] * cantidad
            ejecutar("INSERT INTO historial_ventas (nombre_prod, cantidad, total) VALUES (%s, %s, %s)",
                     (producto["nombre_prod"], cantidad, total))
            ejecutar("UPDATE productos SET stock_actual = stock_actual - %s WHERE id_prod=%s", (cantidad, producto["id_prod"]))
            flash("Venta registrada y stock actualizado.", "success")
        return redirect(url_for("ventas"))
    movimientos = consultar("SELECT * FROM historial_ventas ORDER BY fecha DESC")
    productos = consultar("SELECT * FROM productos ORDER BY nombre_prod")
    resumen = consultar("""SELECT
        COALESCE(SUM(CASE WHEN DATE(fecha)=CURDATE() THEN total ELSE 0 END), 0) AS total,
        COALESCE(SUM(CASE WHEN DATE(fecha)=CURDATE() THEN cantidad ELSE 0 END), 0) AS unidades
        FROM historial_ventas""", uno=True)
    return render_template("ventas.html", movimientos=movimientos, productos=productos, resumen=resumen)


@app.post("/ventas/<int:id_venta>/eliminar")
def eliminar_venta(id_venta):
    ejecutar("DELETE FROM historial_ventas WHERE id_venta=%s", (id_venta,))
    flash("Venta eliminada del historial. El stock no se modifica automáticamente.", "warning")
    return redirect(url_for("ventas"))


if __name__ == "__main__":
    preparar_esquema()
    app.run(debug=True)

