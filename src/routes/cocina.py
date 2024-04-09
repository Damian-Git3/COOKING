from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models import SolicitudProduccion, Receta, Insumo, InsumosReceta
from database.models import db

cocina = Blueprint('cocina', __name__, url_prefix="/cocina")


@cocina.route('/cocinar')
@login_required
def cocinar():
    solicitudesProduccion = SolicitudProduccion.query.all()
    return render_template('modulos/cocina/cocinar.html', solicitudesProduccion=solicitudesProduccion)

@cocina.route('/recetas')
@login_required
def recetas():
    return render_template('modulos/cocina/recetas.html')

@cocina.route('/lotes/insumos')
@login_required
def lotes_insumos():
    return render_template('modulos/cocina/recetas.html')


@cocina.route("/aceptar-solicitud/<int:idSolicitud>")
@login_required
def aceptarSolicitud(idSolicitud):
    print("--------------------")
    print("Aceptando solicitud:", idSolicitud)

    solicitudProduccion = SolicitudProduccion.query.get(idSolicitud)

    if solicitudProduccion:
        solicitudProduccion.status = 2
        solicitudProduccion.idUsuarioProduccion = current_user.id
        db.session.commit()

        insumosReceta = InsumosReceta.query.filter_by(
            idReceta=solicitudProduccion.idReceta).all()
        
        receta = Receta.query.get(solicitudProduccion.idReceta)

        mensajeReceta = f"Descripción receta: \n{receta.descripcion}\n\n"
        mensajeReceta += "Los ingredientes para esta receta son:\n"

        for insumoReceta in insumosReceta:
            insumo = Insumo.query.get(insumoReceta.idInsumo)
            mensajeReceta += f"{insumo.nombre}: {insumoReceta.cantidad} {insumo.unidad_medida}\n"

        print(mensajeReceta)
        flash(mensajeReceta, 'receta')
        return redirect(url_for('cocina.solicitudesProduccion'))
    else:
        flash("No se encontro la solicitud de producción con los datos proporcionados", 'info')
        return redirect(url_for('cocina.solicitudesProduccion'))

