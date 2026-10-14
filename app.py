import os
from contextlib import closing
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, url_for
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__, template_folder="temples", static_folder="static")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(32)

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


def requiere_sesion(funcion):
    @wraps(funcion)
    def decorada(*args, **kwargs):
        if not session.get("id_usuario"):
            return redirect(url_for("login", next=request.path))
        if (not session.get("terminos_aceptados")
                and request.endpoint not in {"mostrar_terminos", "aceptar_terminos"}):
            return redirect(url_for("mostrar_terminos"))
        return funcion(*args, **kwargs)
    return decorada


def registrar_sesion(id_usuario, email):
    session.clear()
    session["id_usuario"] = id_usuario
    session["email"] = email


def mensaje_error_base_datos():
    app.logger.exception("Falló una operación de base de datos")
    flash(
        "No se pudo acceder a MySQL. Revisá que el servidor esté iniciado y que "
        "DB_HOST, DB_USER y DB_PASSWORD en .env sean correctos.",
        "danger"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("id_usuario"):
        return redirect(url_for("inicio"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        try:
            usuario = consultar(
                "SELECT id_usuario, email, password_hash FROM usuarios WHERE email=%s",
                (email,), uno=True
            )
        except mysql.connector.Error:
            mensaje_error_base_datos()
            return render_template("auth.html", registro=False), 503
        if usuario and check_password_hash(usuario["password_hash"], password):
            registrar_sesion(usuario["id_usuario"], usuario["email"])
            destino = request.args.get("next", "")
            if destino.startswith("/") and not destino.startswith("//"):
                return redirect(destino)
            return redirect(url_for("mostrar_terminos"))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("auth.html", registro=False)


@app.route("/registro-inicial", methods=["GET", "POST"])
def registro_inicial():
    try:
        usuarios = consultar("SELECT COUNT(*) AS total FROM usuarios", uno=True)["total"]
    except mysql.connector.Error:
        mensaje_error_base_datos()
        return render_template("auth.html", registro=True), 503
    if usuarios:
        flash("La creación inicial de cuenta ya fue completada.", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmacion = request.form.get("confirmacion", "")
        if not email or "@" not in email:
            flash("Ingresá un correo válido.", "danger")
        elif len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
        elif password != confirmacion:
            flash("Las contraseñas no coinciden.", "danger")
        else:
            try:
                id_usuario = ejecutar(
                    "INSERT INTO usuarios (email, password_hash) VALUES (%s, %s)",
                    (email, generate_password_hash(password))
                )
                registrar_sesion(id_usuario, email)
                flash("Cuenta creada. Ya podés empezar a usar CoopProa.", "success")
                return redirect(url_for("mostrar_terminos"))
            except mysql.connector.IntegrityError:
                flash("Ese correo ya está registrado.", "danger")
            except mysql.connector.Error:
                mensaje_error_base_datos()
    return render_template("auth.html", registro=True)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/")
@requiere_sesion
def inicio():
    if not session.get("terminos_aceptados"):
        return redirect(url_for("mostrar_terminos"))

    resumen = {
        "productos": consultar(
            "SELECT COUNT(*) AS total FROM productos",
            uno=True
        )["total"],
        "proveedores": consultar(
            "SELECT COUNT(*) AS total FROM proveedores",
            uno=True
        )["total"],
        "ventas_hoy": consultar(
            """SELECT COALESCE(SUM(total), 0) AS total
               FROM historial_ventas WHERE DATE(fecha) = %s""",
            (date.today(),),
            uno=True
        )["total"],
    }
    return render_template("index.html", resumen=resumen)


@app.route("/aceptar-terminos")
@requiere_sesion
def mostrar_terminos():
    if session.get("terminos_aceptados"):
        return redirect(url_for("inicio"))
    return render_template("aceptar_terminos.html")


@app.route("/decidir-terminos", methods=["POST"])
@requiere_sesion
def aceptar_terminos():
    decision = request.form.get("decision")

    if decision == "aceptar" and request.form.get("acepto") == "si":
        session["terminos_aceptados"] = True
        return redirect(url_for("inicio"))

    session.pop("terminos_aceptados", None)
    return render_template(
        "aceptar_terminos.html",
        rechazado=True
    )

@app.route("/terminos")
def terminos():
    return render_template("terminos.html")


@app.route("/privacidad")
def privacidad():
    return render_template("privacidad.html")


@app.route("/inventario", methods=["GET", "POST"])
@requiere_sesion
def inventario():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre_prod", "").strip()
            categoria = request.form.get("categoria", "General").strip() or "General"
            precio_costo = Decimal(request.form.get("precio_costo", "").strip() or "0")
            porcentaje = Decimal(request.form.get("porcentaje_ganancia", "").strip() or "0")
            precio_venta = Decimal(request.form.get("precio_venta", "").strip() or "0")
            stock = int(request.form.get("stock_actual", "0"))
            if not nombre:
                raise ValueError("Ingresá el nombre del producto.")
            if min(precio_costo, porcentaje, precio_venta) < 0 or stock < 0:
                raise ValueError("Los precios, porcentajes y el stock no pueden ser negativos.")
            ejecutar(
                """INSERT INTO productos
                   (nombre_prod, categoria, precio_costo, porcentaje_ganancia, precio_venta, stock_actual)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (nombre, categoria, precio_costo, porcentaje, precio_venta, stock),
            )
            flash("Producto creado correctamente.", "success")
        except (InvalidOperation, TypeError, ValueError):
            flash("Revisá los precios, el porcentaje y el stock ingresados.", "danger")
        except mysql.connector.Error:
            app.logger.exception("Falló el alta de producto en MySQL")
            flash("MySQL no pudo guardar el producto. Verificá el esquema de la tabla productos.", "danger")
        return redirect(url_for("inventario"))
    productos = consultar("SELECT * FROM productos ORDER BY nombre_prod")
    return render_template("inventario.html", productos=productos)


@app.post("/inventario/<int:id_prod>/editar")
@requiere_sesion
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
@requiere_sesion
def eliminar_producto(id_prod):
    try:
        ejecutar("DELETE FROM productos WHERE id_prod=%s", (id_prod,))
        flash("Producto eliminado.", "success")
    except mysql.connector.IntegrityError:
        flash("No se puede eliminar un producto con ventas o compras asociadas.", "danger")
    return redirect(url_for("inventario"))


@app.route("/proveedores", methods=["GET", "POST"])
@requiere_sesion
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
    productos = consultar("SELECT id_prod, nombre_prod, stock_actual FROM productos ORDER BY nombre_prod")
    return render_template("proveedores.html", proveedores=datos, productos=productos)


@app.post("/compras")
@requiere_sesion
def registrar_compra():
    id_prov = request.form.get("id_prov", type=int)
    id_prod = request.form.get("id_prod", type=int)
    cantidad = request.form.get("cantidad", type=int)
    precio_pago = request.form.get("precio_pago", type=float)
    if not id_prov or not id_prod or not cantidad or cantidad < 1 or precio_pago is None or precio_pago < 0:
        flash("Revisá proveedor, producto, cantidad y precio de compra.", "danger")
        return redirect(url_for("proveedores"))
    conexion = conectar_db()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO pagos_a_proveedores (id_prov, id_prod, id_usuario, cantidad, precio_pago) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_prov, id_prod, session["id_usuario"], cantidad, precio_pago)
        )
        cursor.execute(
            "UPDATE productos SET stock_actual = stock_actual + %s WHERE id_prod=%s",
            (cantidad, id_prod)
        )
        if cursor.rowcount != 1:
            raise ValueError("El producto seleccionado ya no existe.")
        conexion.commit()
        flash("Compra registrada y stock actualizado.", "success")
    except (mysql.connector.Error, ValueError) as error:
        conexion.rollback()
        flash(str(error) if isinstance(error, ValueError) else "No se pudo registrar la compra.", "danger")
    finally:
        conexion.close()
    return redirect(url_for("proveedores"))


@app.post("/proveedores/<int:id_prov>/editar")
@requiere_sesion
def editar_proveedor(id_prov):
    ejecutar("UPDATE proveedores SET nombre_prov=%s, contacto=%s WHERE id_prov=%s",
             (request.form["nombre_prov"], request.form.get("contacto", ""), id_prov))
    flash("Proveedor actualizado correctamente.", "success")
    return redirect(url_for("proveedores"))


@app.post("/proveedores/<int:id_prov>/eliminar")
@requiere_sesion
def eliminar_proveedor(id_prov):
    try:
        ejecutar("DELETE FROM proveedores WHERE id_prov=%s", (id_prov,))
        flash("Proveedor eliminado.", "success")
    except mysql.connector.IntegrityError:
        flash("No se puede eliminar un proveedor con compras asociadas.", "danger")
    return redirect(url_for("proveedores"))


@app.route("/ventas", methods=["GET", "POST"])
@requiere_sesion
def ventas():
    if request.method == "POST":
        producto = consultar("SELECT * FROM productos WHERE id_prod=%s", (request.form["id_prod"],), uno=True)
        cantidad = request.form.get("cantidad", type=int)
        if not cantidad or cantidad < 1:
            flash("La cantidad debe ser mayor que cero.", "danger")
        elif not producto or producto["stock_actual"] < cantidad:
            flash("No hay stock suficiente para registrar la venta.", "danger")
        else:
            total = producto["precio_venta"] * cantidad
            conexion = conectar_db()
            try:
                cursor = conexion.cursor()
                cursor.execute(
                    "UPDATE productos SET stock_actual=stock_actual-%s "
                    "WHERE id_prod=%s AND stock_actual >= %s",
                    (cantidad, producto["id_prod"], cantidad)
                )
                if cursor.rowcount != 1:
                    raise ValueError("El stock cambió y ya no alcanza para esta venta.")
                cursor.execute(
                    "INSERT INTO historial_ventas (id_usuario, id_prod, cantidad, total) "
                    "VALUES (%s, %s, %s, %s)",
                    (session["id_usuario"], producto["id_prod"], cantidad, total)
                )
                conexion.commit()
                flash("Venta registrada y stock actualizado.", "success")
            except (mysql.connector.Error, ValueError) as error:
                conexion.rollback()
                flash(str(error) if isinstance(error, ValueError) else "No se pudo registrar la venta.", "danger")
            finally:
                conexion.close()
        return redirect(url_for("ventas"))
    movimientos = consultar(
        "SELECT v.*, p.nombre_prod FROM historial_ventas v "
        "JOIN productos p ON p.id_prod=v.id_prod ORDER BY v.fecha DESC"
    )
    productos = consultar("SELECT * FROM productos ORDER BY nombre_prod")
    mas_vendidos = consultar(
        "SELECT p.id_prod, p.nombre_prod, SUM(v.cantidad) AS unidades, "
        "SUM(v.total) AS total FROM historial_ventas v "
        "JOIN productos p ON p.id_prod=v.id_prod "
        "GROUP BY p.id_prod, p.nombre_prod ORDER BY unidades DESC LIMIT 3"
    )
    stock_bajo = consultar(
        "SELECT id_prod, nombre_prod, stock_actual FROM productos "
        "WHERE stock_actual <= 5 ORDER BY stock_actual, nombre_prod LIMIT 4"
    )
    resumen = consultar("""SELECT
        COALESCE(SUM(CASE WHEN DATE(fecha)=CURDATE() THEN total ELSE 0 END), 0) AS total,
        COALESCE(SUM(CASE WHEN DATE(fecha)=CURDATE() THEN cantidad ELSE 0 END), 0) AS unidades
        FROM historial_ventas""", uno=True)
    return render_template(
        "ventas.html", movimientos=movimientos, productos=productos,
        resumen=resumen, mas_vendidos=mas_vendidos, stock_bajo=stock_bajo
    )


@app.post("/ventas/<int:id_venta>/eliminar")
@requiere_sesion
def eliminar_venta(id_venta):
    conexion = conectar_db()
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_prod, cantidad FROM historial_ventas WHERE id_venta=%s", (id_venta,))
        venta = cursor.fetchone()
        if venta:
            cursor.execute("DELETE FROM historial_ventas WHERE id_venta=%s", (id_venta,))
            cursor.execute(
                "UPDATE productos SET stock_actual=stock_actual+%s WHERE id_prod=%s",
                (venta[1], venta[0])
            )
            conexion.commit()
            flash("Venta eliminada y stock restaurado.", "success")
    except mysql.connector.Error:
        conexion.rollback()
        flash("No se pudo eliminar la venta.", "danger")
    finally:
        conexion.close()
    return redirect(url_for("ventas"))


@app.route("/app.js")
def app_js():
    return send_from_directory(os.path.dirname(__file__), "app.js")


@app.route("/inventario.js")
def inventario_js():
    return send_from_directory(os.path.dirname(__file__), "inventario.js")


if __name__ == "__main__":
    app.run(debug=True)

