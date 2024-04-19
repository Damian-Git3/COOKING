from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import desc, extract, func

from database.models import DetalleVenta, LoteGalleta, Receta, Usuario, Venta, db
from logger import logger as log

dashboard = Blueprint(
    "dashboard", __name__, url_prefix="/dashboard", template_folder="templates"
)


@dashboard.route("/")
@login_required
def index():

    galletas_ventas_mes = obtener_galletas_vendidas_por_mes()
    ventas_mes = obtener_ventas_por_mes()
    ventas_totales_mes = obtener_total_ventas_por_mes()
    galletas_tipos = obtener_galletas_vendidas_por_tipo()
    ventas_vendedor = obtener_ventas_vendedor()
    numero_ventas_vendedor = obtener_numero_total_ventas_por_vendedor()

    return render_template(
        "dashboard/dashboard.html",
        galletaVentasMes=galletas_ventas_mes,
        ventasMes=ventas_mes,
        ventasTotalesMes=ventas_totales_mes,
        galletasTipos=galletas_tipos,
        ventasVendedor=ventas_vendedor,
        numeroVentasVendedor=numero_ventas_vendedor,
    )


def obtener_galletas_vendidas_por_mes():
    """
    Obtiene el número de galletas vendidas por mes del año actual, en un arreglo ordenado por mes.
    """
    # Obtener el año actual
    año_actual = datetime.now().year

    # Realizar la consulta
    resultados = (
        db.session.query(
            func.sum(DetalleVenta.cantidad),  # Sumar la cantidad de galletas vendidas
            func.extract("month", Venta.fecha_venta).label(
                "mes"
            ),  # Extraer el mes de la fecha de venta
        )
        .join(
            Venta,
            Venta.id == DetalleVenta.idVenta,  # Unir las tablas Venta y DetalleVenta
        )
        .filter(
            func.extract("year", Venta.fecha_venta)
            == año_actual  # Filtrar por el año actual
        )
        .group_by("mes")  # Agrupar por mes
        .order_by("mes")  # Ordenar por mes
        .all()
    )

    # Inicializar un arreglo de 12 elementos con ceros
    galletas_vendidas_por_mes = [0] * 12

    # Llenar el arreglo con los totales de galletas vendidas por mes
    for resultado in resultados:
        mes = (
            resultado.mes - 1
        )  # Ajustar el índice para que Enero sea el primer elemento
        galletas_vendidas_por_mes[mes] = int(resultado[0])

    return galletas_vendidas_por_mes


def obtener_ventas_por_mes():
    """
    Obtiene el total de ventas por mes del año actual, en un arreglo ordenado por mes.
    """
    # Obtener el año actual
    año_actual = datetime.now().year

    # Realizar la consulta
    resultados = (
        db.session.query(
            func.sum(Venta.total_venta),  # Sumar el total de ventas
            func.extract("month", Venta.fecha_venta).label(
                "mes"
            ),  # Extraer el mes de la fecha de venta
        )
        .filter(
            func.extract("year", Venta.fecha_venta)
            == año_actual  # Filtrar por el año actual
        )
        .group_by("mes")  # Agrupar por mes
        .order_by("mes")  # Ordenar por mes
        .all()
    )

    # Inicializar un arreglo de 12 elementos con ceros
    ventas_por_mes = [0] * 12

    # Llenar el arreglo con los totales de ventas por mes
    for resultado in resultados:
        mes = (
            resultado.mes - 1
        )  # Ajustar el índice para que Enero sea el primer elemento
        # Convertir el objeto Decimal a flotante
        ventas_por_mes[mes] = float(resultado[0])

    return ventas_por_mes


def obtener_total_ventas_por_mes():
    """
    Obtiene el total de ventas realizadas por mes del año actual, en un arreglo ordenado por mes.
    """
    # Obtener el año actual
    año_actual = datetime.now().year

    # Realizar la consulta
    resultados = (
        db.session.query(
            func.count(Venta.id),  # Contar el número de ventas
            func.extract("month", Venta.fecha_venta).label(
                "mes"
            ),  # Extraer el mes de la fecha de venta
        )
        .filter(
            func.extract("year", Venta.fecha_venta)
            == año_actual  # Filtrar por el año actual
        )
        .group_by("mes")  # Agrupar por mes
        .order_by("mes")  # Ordenar por mes
        .all()
    )

    # Inicializar un arreglo de 12 elementos con ceros
    total_ventas_por_mes = [0] * 12

    # Llenar el arreglo con los totales de ventas por mes
    for resultado in resultados:
        mes = (
            resultado.mes - 1
        )  # Ajustar el índice para que Enero sea el primer elemento
        total_ventas_por_mes[mes] = resultado[0]

    return total_ventas_por_mes


def obtener_galletas_vendidas_por_tipo():
    """
    Obtiene el número de galletas vendidas por tipo de galleta (nombre de la receta),
    incluyendo las galletas con ventas de 0.
    """
    # Realizar la consulta
    resultados = (
        db.session.query(
            Receta.nombre,  # Nombre de la receta (tipo de galleta)
            func.coalesce(func.sum(DetalleVenta.cantidad), 0).label(
                "cantidad_vendida"
            ),  # Sumar la cantidad de galletas vendidas, usando 0 si no hay ventas
        )
        .outerjoin(
            LoteGalleta, LoteGalleta.idReceta == Receta.id  # Unir con LoteGalleta
        )
        .outerjoin(
            DetalleVenta,
            DetalleVenta.idStock == LoteGalleta.id,  # Unir con DetalleVenta
        )
        .outerjoin(Venta, Venta.id == DetalleVenta.idVenta)  # Unir con Venta
        .group_by(Receta.nombre)  # Agrupar por el nombre de la receta
        .all()
    )

    # Convertir los resultados a un diccionario para facilitar su uso
    galletas_vendidas_por_tipo = {
        resultado.nombre: resultado.cantidad_vendida for resultado in resultados
    }

    return galletas_vendidas_por_tipo


def obtener_ventas_vendedor():
    """
    Obtiene el total de ventas por cada usuario del año actual.
    """
    # Obtener el año actual
    anio_actual = datetime.now().year

    # Realizar la consulta
    resultados = (
        db.session.query(
            Usuario.nombre,  # Nombre del usuario
            func.sum(Venta.total_venta).label(
                "total_ventas"
            ),  # Sumar el total de ventas
        )
        .join(Venta, Venta.idUsuario == Usuario.id)  # Unir las tablas Venta y Usuario
        .filter(
            func.extract("year", Venta.fecha_venta)
            == anio_actual  # Filtrar por el año actual
        )
        .group_by(Usuario.nombre)  # Agrupar por el nombre del usuario
        .order_by(
            desc("total_ventas")
        )  # Ordenar por el total de ventas en orden descendente
        .all()
    )

    # Convertir los resultados a un diccionario para facilitar su uso
    ventas_por_vendedor = {
        resultado.nombre: resultado.total_ventas for resultado in resultados
    }

    return ventas_por_vendedor


def obtener_numero_total_ventas_por_vendedor():
    """
    Obtiene el número total de ventas por cada usuario del año actual.
    """
    # Obtener el año actual
    anio_actual = datetime.now().year

    # Realizar la consulta
    resultados = (
        db.session.query(
            Usuario.nombre,  # Nombre del usuario
            func.count(Venta.id).label(
                "numero_total_ventas"
            ),  # Contar el número total de ventas
        )
        .join(Venta, Venta.idUsuario == Usuario.id)  # Unir las tablas Venta y Usuario
        .filter(
            func.extract("year", Venta.fecha_venta)
            == anio_actual  # Filtrar por el año actual
        )
        .group_by(Usuario.nombre)  # Agrupar por el nombre del usuario
        .order_by(
            desc("numero_total_ventas")
        )  # Ordenar por el número total de ventas en orden descendente
        .all()
    )

    # Convertir los resultados a un diccionario para facilitar su uso
    numero_total_ventas_por_vendedor = {
        resultado.nombre: resultado.numero_total_ventas for resultado in resultados
    }

    return numero_total_ventas_por_vendedor
