from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a MySQL
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root", # Configurar según su usuario de MySQL
        password="12345", # Configurar según su contraseña
        database="coopproa_db" # La base de datos del ejercicio anterior
    )

