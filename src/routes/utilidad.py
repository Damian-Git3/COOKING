""" Rutas de la sección de utilidad """

from flask import Blueprint, render_template, request, redirect, url_for, flash

utilidad = Blueprint("utilidad", __name__, url_prefix="/utilidad")


@utilidad.route("/")
def inicio():
    """Ruta para la página de inicio de la sección de utilidad"""
    return render_template("utilidad/utilidad.html")
