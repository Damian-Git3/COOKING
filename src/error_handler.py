""" Modulo que se encarga de manejar los errores de la aplicacion """


from flask import render_template

from logger import logger as log


def page_not_found(e):
    """Funcion que se encarga de manejar los errores 404"""
    log.error(e)
    return render_template("404.html"), 404


def internal_server_error(e):
    """Funcion que se encarga de manejar los errores 500"""
    log.error(e)
    return (
        render_template(
            "error_page.html",
            error="500",
            mensaje="Error del servidor porfavor intentelo más tarde",
        ),
        500,
    )


def forbidden(e):
    """Funcion que se encarga de manejar los errores 403"""
    log.error(e)
    return render_template("error_page.html", error="403", mensaje="Prohibido"), 403


def unauthorized(e):
    """Funcion que se encarga de manejar los errores 401"""
    log.error(e)
    return (
        render_template("error_page.html", error="401", mensaje="No autorizado"),
        401,
    )


def bad_request(e):
    """Funcion que se encarga de manejar los errores 400"""
    log.error(e)
    return (
        render_template("error_page.html", error="400", mensaje="Petición incorrecta"),
        400,
    )


def method_not_allowed(e):
    """Funcion que se encarga de manejar los errores 405"""
    log.error(e)
    return (
        render_template("error_page.html", error="405", mensaje="Método no autorizado"),
        405,
    )


def attribute_error(e):
    """Funcion que se encarga de manejar los errores de atributos"""
    log.error(e)
    return render_template(
        "error_page.html", error="500", mensaje="Error en la carga de los atributos"
    )


def zero_division_error(e):
    """Funcion que se encarga de manejar los errores de division entre cero"""
    log.error(e)
    return render_template(
        "error_page.html", error="500", mensaje="Se generó una división entre cero"
    )


def import_error(e):
    """Funcion que se encarga de manejar los errores de importación"""
    log.error(e)
    return render_template(
        "error_page.html", error="500", mensaje="Error de importación"
    )


def not_implemented_error(e):
    """Funcion que se encarga de manejar los errores de implementación"""
    log.error(e)
    return render_template(
        "error_page.html", error="500", mensaje="Error de implementación"
    )


def type_error(e):
    """Funcion que se encarga de manejar los errores de tipo de dato"""
    log.error(e)
    return (
        render_template(
            "error_page.html", error="500", mensaje="Error en el tipo de dato"
        )
    ), 500


def integrity_error(e):
    """Funcion que se encarga de manejar los errores de integridad"""
    return (
        render_template("error_page.html", error="500", mensaje="Error de integridad")
    ), 500


def value_error(e):
    """Funcion que se encarga de manejar los errores de valor"""
    return (
        render_template("error_page.html", error="500", mensaje="Error de valor")
    ), 500


def sqlalchemy_error(e):
    """Funcion que se encarga de manejar los errores de sqlalchemy"""
    log.error(e)
    return (
        render_template("error_page.html", error="500", mensaje="Error de modficación")
    ), 500


def exception_error(e):
    """Funcion que se encarga de manejar los errores de excepción"""
    log.error(e)
    return (
        render_template("error_page.html", error="500", mensaje="Error muy inesperado")
    ), 500
