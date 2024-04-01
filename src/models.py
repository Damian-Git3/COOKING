
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

asignacion_rol_usuario = db.Table('asignaciones_rol_usuario',
    db.Column('idUsuario', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('idRol', db.Integer, db.ForeignKey('roles.id'))
)

class Rol(db.Model):
    __tablename__="roles"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    usuarios = db.relationship('Usuario', secondary=asignacion_rol_usuario, back_populates='roles')
    
    # Método para obtener solo el nombre
    def __str__(self):
        return self.nombre
    

class Usuario(UserMixin, db.Model):
    __tablename__="usuarios"
    
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=True)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    #last_login_ip = db.Column(db.String(100))
    #current_login_ip = db.Column(db.String(100))
    #login_count = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), default=True)
    is_authenticated = db.Column(db.Boolean(), default=True)
    is_anonymous = db.Column(db.Boolean(), default=False)
    estatus = db.Column(db.Boolean(), nullable=False, default=True)
    #fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    
    roles = db.relationship('Rol', secondary=asignacion_rol_usuario, back_populates='usuarios')
    
    # Método para obtener solo el nombre
    def __str__(self):
        return self.nombre
    
    #metodo para flask-login
    def get_id(self):
        return str(self.id)
    
    #metodo para acelerar la validacion de roles
    def has_roles(self, role):
        return bool(Rol.query.join(Rol.usuarios).filter_by(nombre=role and Usuario.id == self.id).first())
    

class Insumo(db.Model):
    __tablename__ = 'insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.String(45), nullable=False)
    unidad_medida = db.Column(db.String(45), nullable=False)
    cantidad_maxima = db.Column(db.Float, nullable=False)
    cantidad_minima = db.Column(db.Float, nullable=False)
    merma = db.Column(db.Float, nullable=False)
    
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(45), nullable=False)
    direccion = db.Column(db.String(45), nullable=False)
    nombre_proveedor = db.Column(db.String(45), nullable=False)
    
class Receta(db.Model):
    __tablename__ = 'recetas'
    
    id = db.Column(db.Integer, primary_key=True)
    peso_estimado = db.Column(db.Float, nullable=False)
    utilidad = db.Column(db.Float)
    piezas = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(500))
    nombre = db.Column(db.String(50), nullable=False)

class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    pago_proveedor = db.Column(db.Float, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    idTransaccionCaja = db.Column(db.Integer, primary_key=True)
    idProveedores = db.Column(db.Integer, db.ForeignKey('proveedores.id'), primary_key=True)
    
class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.DateTime, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    idProveedores = db.Column(db.Integer, db.ForeignKey('proveedores.id'), primary_key=True)

class CorteCaja(db.Model):
    __tablename__ = 'cortes_caja'
    
    id = db.Column(db.Integer, primary_key=True)
    monto_final = db.Column(db.Float)
    monto_inicial = db.Column(db.Float)
    fecha_corte = db.Column(db.Date)

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer)
    
    idVenta = db.Column(db.Integer, db.ForeignKey('ventas.id'), primary_key=True)
    idStock = db.Column(db.Integer, db.ForeignKey('lotes_galletas.id'), primary_key=True)

class IngredienteReceta(db.Model):
    __tablename__ = 'ingredientes_receta'
    
    cantidad = db.Column(db.Float, nullable=False)
    
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.id'), primary_key=True)
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.id'), primary_key=True)

class LogAccion(db.Model):
    __tablename__ = 'logs_acciones'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    modulo = db.Column(db.String(45), nullable=False)
    detalles = db.Column(db.String(200), nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LogLogin(db.Model):
    __tablename__ = 'logs_login'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    exito = db.Column(db.Boolean, nullable=False)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LoteGalleta(db.Model):
    __tablename__ = 'lotes_galletas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_entrada = db.Column(db.Date)
    cantidad = db.Column(db.Integer, nullable=False)
    merma = db.Column(db.Integer)
    tipo_venta = db.Column(db.Integer, nullable=False)
    
    idProduccion = db.Column(db.Integer, db.ForeignKey('solicitudes_produccion.id'), nullable=False)
    idReceta = db.Column(db.Integer, nullable=False)
    idUsuarios = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class LoteInsumo(db.Model):
    __tablename__ = 'lotes_insumo'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    precio_unidad = db.Column(db.Float, nullable=False)
    
    idInsumo = db.Column(db.Integer, db.ForeignKey('insumos.id'), primary_key=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('compras.id'), primary_key=True)

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitudes_produccion'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_produccion = db.Column(db.Date, nullable=False)
    mensaje = db.Column(db.String(50))
    status = db.Column(db.Boolean)
    tandas = db.Column(db.Integer)
    merma = db.Column(db.Integer)
    fecha_solicitud = db.Column(db.Date)
    
    idReceta = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    idUsuarioSolictud = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    idUsuarioProduccion = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class TransaccionCaja(db.Model):
    __tablename__ = 'transacciones_caja'
    
    id = db.Column(db.Integer, primary_key=True)
    monto_egreso = db.Column(db.Float)
    monto_ingreso = db.Column(db.Float)
    fecha_transaccion = db.Column(db.Date)
    
    idCorteCaja = db.Column(db.Integer, db.ForeignKey('cortes_caja.id'), nullable=False)
