from flask import Blueprint, Flask, request,render_template, Response, redirect, url_for
from flask_login import login_required, current_user

from flask_wtf.csrf import CSRFProtect
from flask import g
from flask import flash, jsonify
from configu.config import DevelopmentConfig
from database.models import db, Usuario, Rol, asignacion_rol_usuario, Insumo, Receta, SolicitudProduccion, Venta, DetalleVenta, Compra, Proveedor, LoteGalleta

from forms import forms
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, extract,text
from datetime import datetime, timedelta

venta = Blueprint('venta', __name__, url_prefix="/venta")


@venta.route('/compras')
@login_required
def compras():
    return render_template('modulos/venta/compras.html')



@venta.route('/punto_venta')
@login_required
def punto_venta():
    return render_template('modulos/venta/punto-venta.html')

@venta.route('/solicitud_produccion')
@login_required
def solicitud_produccion():
    form = forms.SolicitudProduccionForm(request.form)
    
    # Obtiene todas las recetas de la base de datos
    recetas = Receta.query.all()
    
    # Crea una lista de tuplas con el ID y el nombre de cada receta
    recetas_opciones = [(receta.id, receta.nombre) for receta in recetas]
    recetas_imagenes = [(receta.id, receta.imagen) for receta in recetas]
    
    # Asigna las opciones al campo receta del formulario
    form.receta.choices = recetas_opciones
    
    solicitudes = SolicitudProduccion.query.options(
        joinedload(SolicitudProduccion.receta), # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud), # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion) # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
    ).all()
        
    return render_template('modulos/venta/solicitudes-produccion.html', form=form, recetas_imagenes=recetas_imagenes, solicitudes=solicitudes)

@venta.route('/solicitud_produccion/nuevo')
@login_required
def solicitud_produccion_nuevo():
    form = forms.SolicitudProduccionForm(request.form)
    
    # Obtiene todas las recetas de la base de datos
    recetas = Receta.query.all()
    
    # Crea una lista de tuplas con el ID y el nombre de cada receta
    recetas_opciones = [(receta.id, receta.nombre) for receta in recetas]
    recetas_imagenes = [(receta.id, receta.imagen) for receta in recetas]
    
    # Asigna las opciones al campo receta del formulario
    form.receta.choices = recetas_opciones
    
    solicitudes = SolicitudProduccion.query.options(
        joinedload(SolicitudProduccion.receta), # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud), # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion) # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
    ).all()

        
    return render_template('modulos/venta/solicitudes-produccion.html', form=form, recetas_imagenes=recetas_imagenes, solicitudes=solicitudes, nuevo=True)

@venta.route('/solicitud_produccion/nuevo', methods=['POST'])
@login_required
def solicitud_produccion_post():
    form = forms.SolicitudProduccionForm(request.form)
    
    # Obtiene todas las recetas de la base de datos
    recetas = Receta.query.all()
    
    # Crea una lista de tuplas con el ID y el nombre de cada receta
    recetas_opciones = [(receta.id, receta.nombre) for receta in recetas]
    recetas_imagenes = [(receta.id, receta.imagen) for receta in recetas]
    
    # Asigna las opciones al campo receta del formulario
    form.receta.choices = recetas_opciones
    
    if form.validate():
        rol_cocinero = Rol.query.filter_by(nombre='cocinero').first()

        usuario_cocinero=0
        if rol_cocinero is not None:
            # Luego, filtra los usuarios que tienen el rol 'cocinero' y ordena por 'is_active'
            usuario_cocinero = Usuario.query.join(asignacion_rol_usuario).join(Rol).filter(Rol.id == rol_cocinero.id).order_by(desc('is_active')).first()

            # Si no se encuentra un usuario cocinero con is_active, intenta obtener el usuario con el last_login_at más reciente
            if usuario_cocinero is None:
                usuario_cocinero = Usuario.query.join(asignacion_rol_usuario).join(Rol).filter(Rol.id == rol_cocinero.id).order_by(desc('last_login_at')).first()

            if usuario_cocinero is not None:
                usuario_cocinero = usuario_cocinero.id
            else:
                    # Maneja el caso en que no se encuentre ningún usuario cocinero
                usuario_cocinero = current_user.id
        
        solicitud = SolicitudProduccion(
            idReceta=form.receta.data,
            idUsuarioSolicitud=current_user.id,
            idUsuarioProduccion=usuario_cocinero,
            fecha_solicitud=form.fecha_solicitud.data,
            tandas=form.tandas.data,
            status=1
        )
        
        db.session.add(solicitud)
        db.session.commit()
        
        flash('Solicitud de producción creada correctamente', 'success')
    
    
    solicitudes = SolicitudProduccion.query.options(
        joinedload(SolicitudProduccion.receta), # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud), # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion) # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
    ).all()
    
    return redirect(url_for('venta.solicitud_produccion'))

@venta.route('/solicitud_produccion/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_solicitud_produccion(id):
    form2 = forms.ModificarSolicitudProduccionForm(request.form)
    form = forms.SolicitudProduccionForm(request.form)
    
    if request.method == 'POST' and form2.validate():
        
        solicitud = SolicitudProduccion.query.get(id)
        solicitud.tandas = form.tandas.data
        solicitud.fecha_solicitud = form.fecha_solicitud.data
        solicitud.mensaje = form2.mensaje.data
        db.session.commit()
        flash('Solicitud de producción modificada correctamente', 'success')
        return redirect(url_for('venta.solicitud_produccion'))
        
    # Obtiene todas las recetas de la base de datos
    recetas = Receta.query.all()
    
    # Crea una lista de tuplas con el ID y el nombre de cada receta
    recetas_opciones = [(receta.id, receta.nombre) for receta in recetas]
    recetas_imagenes = [(receta.id, receta.imagen) for receta in recetas]
    
    # Asigna las opciones al campo receta del formulario
    form.receta.choices = recetas_opciones
    
    solicitudes = SolicitudProduccion.query.options(
        joinedload(SolicitudProduccion.receta), # Asume que 'receta' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioSolicitud), # Asume que 'usuarioSolicitud' es el nombre de la relación en SolicitudProduccion
        joinedload(SolicitudProduccion.usuarioProduccion) # Asume que 'usuarioProduccion' es el nombre de la relación en SolicitudProduccion
    ).all()
    
    # Busca la solicitud de producción específica por su ID
    solicitud_especifica = SolicitudProduccion.query.get(id)

    # Si encontramos la solicitud, obtenemos el nombre de la receta
    nombre_receta = None
    imagen_receta = None
    if solicitud_especifica:
        nombre_receta = solicitud_especifica.receta.nombre
        imagen_receta = solicitud_especifica.receta.imagen
    
    return render_template('modulos/venta/solicitudes-produccion.html', form=form, form2=form2, recetas_imagenes=recetas_imagenes, solicitudes=solicitudes, editar=True,nombre_receta=nombre_receta,imagen_receta = imagen_receta, id_receta=id)

@venta.route('/solicitud_produccion/delete', methods=['POST'])
@login_required
def delete_solicitud_produccion():
    id = request.form.get('id')
    solicitud = SolicitudProduccion.query.get_or_404(id)
    db.session.delete(solicitud)
    db.session.commit()
    flash('Solicitud de producción eliminada correctamente', 'success')
    return redirect(url_for('venta.solicitud_produccion'))


@venta.route('/almacen/galletas', methods=['GET', 'POST'])
def lotes_galletas():
    form = forms.BusquedaLoteGalletaForm(request.form)
    
    form.receta.choices = [(0, 'Todas las recetas')] + [(receta.id, receta.nombre) for receta in Receta.query.all()]
    
    if request.method=="POST" and form.validate():
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data
        receta = form.receta.data
        lotes = []
        
        base_query = db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre).join(Receta, LoteGalleta.idReceta == Receta.id).join(Usuario, LoteGalleta.idUsuarios == Usuario.id)
        print(fecha_inicio, fecha_fin, receta)
        if receta == 0:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.cantidad > 0
            ).all()
        else:
            lotes = base_query.filter(
                LoteGalleta.fecha_entrada >= fecha_inicio,
                LoteGalleta.fecha_entrada <= fecha_fin,
                LoteGalleta.idReceta == receta,
                LoteGalleta.cantidad > 0
            ).all()
        
        return render_template('modulos/venta/galletas.html', form=form, lotes=lotes, lista=True)
    
    lotes = db.session.query(LoteGalleta, Receta.nombre, Usuario.nombre).join(Receta, LoteGalleta.idReceta == Receta.id).join(Usuario, LoteGalleta.idUsuarios == Usuario.id).filter(LoteGalleta.cantidad > 0).all()
    
    return render_template('modulos/venta/galletas.html', form=form, lotes=lotes, lista = True)

@venta.route('/merma/galletas', methods=['GET','POST'])
def merma_galletas():
    form = forms.MermaGalletaForm(request.form)
    if form.validate():
        tipo_medida = form.tipo_medida.data
        cantidad = form.cantidad.data
        
    return redirect(url_for('venta.lotes_galletas'))
