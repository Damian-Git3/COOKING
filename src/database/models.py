from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, func
from sqlalchemy.schema import Index

db = SQLAlchemy()

asignacion_rol_usuario = db.Table(
    "asignaciones_rol_usuario",
    db.Column("idUsuario", db.Integer, db.ForeignKey("usuarios.id")),
    db.Column("idRol", db.Integer, db.ForeignKey("roles.id")),
)


class RecetaLoteInsumo(db.Model):
    __tablename__ = "receta_lotes_insumos"
    idSolicitud = db.Column(
        db.Integer, db.ForeignKey("solicitudes_produccion.id"), primary_key=True
    )
    idReceta = db.Column(db.Integer, db.ForeignKey("recetas.id"), primary_key=True)
    idLoteInsumo = db.Column(
        db.Integer, db.ForeignKey("lotes_insumo.id"), primary_key=True
    )
    cantidad = db.Column(db.Float, nullable=False)


class InsumosReceta(db.Model):
    __tablename__ = "insumos_receta"
    idReceta = db.Column(db.Integer, db.ForeignKey("recetas.id"), primary_key=True)
    idInsumo = db.Column(db.Integer, db.ForeignKey("insumos.id"), primary_key=True)
    cantidad = db.Column(db.Float, nullable=False)

    receta = db.relationship("Receta", backref="insumos")
    insumo = db.relationship("Insumo", backref="recetas")

    def __str__(self):
        return f"InsumoReceta - idReceta: {self.idReceta}, idInsumo: {self.idReceta},cantidad: {self.cantidad}"


class Receta(db.Model):
    __tablename__ = "recetas"

    id = db.Column(db.Integer, primary_key=True)
    peso_estimado = db.Column(db.Float, nullable=False)
    utilidad = db.Column(db.Float)
    piezas = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(800))
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    imagen = db.Column(db.String(2550))
    estatus = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_nombre_receta", "nombre"),)

    # Método para obtener solo el nombre
    def __str__(self):
        return f"Receta: {self.nombre}, Peso Estimado: {self.peso_estimado}, Piezas: {self.piezas}, Utilidad: {self.utilidad}, Descripcion: {self.descripcion}, Imagen: {self.imagen}, Estatus: {self.estatus}, ID: {self.id}, Insumos: {self.insumos}"

    def serialize(self):
        return {"id": self.id, "nombre": self.nombre, "imagen": self.imagen}


class Insumo(db.Model):
    __tablename__ = "insumos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.String(45), nullable=False)
    unidad_medida = db.Column(Enum("Kilos", "Litros"), nullable=False)
    cantidad_maxima = db.Column(db.Float, nullable=False)
    cantidad_minima = db.Column(db.Float, nullable=False)
    merma = db.Column(db.Float, nullable=False)
    estatus = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_nombre_insumo", "nombre"),)

    def __str__(self):
        return self.nombre + " (" + self.unidad_medida + ")"


class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    usuarios = db.relationship(
        "Usuario", secondary=asignacion_rol_usuario, back_populates="roles"
    )

    __table_args__ = (Index("idx_nombre_rol", "nombre"),)

    # Método para obtener solo el nombre
    def __str__(self):
        return self.nombre


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    contrasenia = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=True)
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    # last_login_ip = db.Column(db.String(100))
    # current_login_ip = db.Column(db.String(100))
    # login_count = db.Column(db.Integer)
    is_active = db.Column(db.Boolean(), default=True)
    is_authenticated = db.Column(db.Boolean(), default=True)
    is_anonymous = db.Column(db.Boolean(), default=False)
    estatus = db.Column(db.Boolean(), nullable=False, default=True)
    # fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)

    roles = db.relationship(
        "Rol", secondary=asignacion_rol_usuario, back_populates="usuarios"
    )

    __table_args__ = (Index("idx_nombre_usuario", "nombre"),)

    # Método para obtener solo el nombre
    def __str__(self):
        return self.nombre

    # metodo para flask-login
    def get_id(self):
        return str(self.id)

    # metodo para acelerar la validacion de roles
    def has_role(self, role):
        return bool(
            Rol.query.join(asignacion_rol_usuario)
            .join(Usuario)
            .filter(Rol.nombre == role, Usuario.id == self.id)
            .first()
        )

    def get_roles(self):
        return [role.nombre for role in self.roles]


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(45), nullable=False, unique=True)
    direccion = db.Column(db.String(45), nullable=False)
    nombre_contacto = db.Column(db.String(45), nullable=False)
    contacto = db.Column(db.String(45), nullable=True)
    estatus = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (Index("idx_empresa_proveedor", "empresa"),)

    # Método para obtener solo el nombre
    def __str__(self):
        return self.empresa


class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pago_proveedor = db.Column(db.Float, nullable=False)
    estatus = db.Column(db.Boolean, nullable=False, default=True)
    fecha_compra = db.Column(db.Date, nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    idTransaccionCaja = db.Column(
        db.Integer, db.ForeignKey("transacciones_caja.id"), nullable=True
    )
    idProveedores = db.Column(
        db.Integer, db.ForeignKey("proveedores.id"), nullable=False
    )

    transaccion = db.relationship(
        "TransaccionCaja",
        foreign_keys=[idTransaccionCaja],
        backref=db.backref("compras_transaccion", lazy="dynamic"),
    )
    proveedor = db.relationship(
        "Proveedor",
        foreign_keys=[idProveedores],
        backref=db.backref("compras_proveedor", lazy="dynamic"),
    )
    lotes_insumo_compra = db.relationship(
        "LoteInsumo",
        back_populates="compra",
    )

    __table_args__ = (Index("idx_fecha_compra", "fecha_compra"),)


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_venta = db.Column(db.DateTime, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)

    idUsuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    idTransaccionCaja = db.Column(
        db.Integer, db.ForeignKey("transacciones_caja.id"), nullable=False
    )
    __table_args__ = (Index("idx_fecha_venta", "fecha_venta"),)


class CorteCaja(db.Model):
    __tablename__ = "cortes_caja"

    id = db.Column(db.Integer, primary_key=True)
    monto_final = db.Column(db.Float, nullable=False, default=1000)
    monto_inicial = db.Column(db.Float, default=1000, nullable=False)
    fecha_corte = db.Column(db.Date, nullable=False, default=datetime.now().date())


class DetalleVenta(db.Model):
    __tablename__ = "detalles_venta"
    id = db.Column(db.Integer, primary_key=True)

    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer)

    idVenta = db.Column(db.Integer, db.ForeignKey("ventas.id"))
    idStock = db.Column(db.Integer, db.ForeignKey("lotes_galletas.id"))


class LogAccion(db.Model):
    __tablename__ = "logs_acciones"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    modulo = db.Column(db.String(45), nullable=False)
    detalles = db.Column(db.String(200), nullable=False)

    idUsuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)


class LogLogin(db.Model):
    __tablename__ = "logs_login"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    exito = db.Column(db.Boolean, nullable=False)

    idUsuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)


class LoteGalleta(db.Model):
    __tablename__ = "lotes_galletas"

    id = db.Column(db.Integer, primary_key=True)
    fecha_entrada = db.Column(db.Date)
    cantidad = db.Column(db.Integer, nullable=False)
    merma = db.Column(db.Integer, nullable=False, default=0)
    tipo_venta = db.Column(db.Integer, nullable=False)
    # agregar el costo de produccion y precio de venta

    idProduccion = db.Column(
        db.Integer, db.ForeignKey("solicitudes_produccion.id"), nullable=False
    )
    idReceta = db.Column(db.Integer, db.ForeignKey("recetas.id"), nullable=False)
    idUsuarios = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    receta = db.relationship(
        "Receta",
        foreign_keys=[idReceta],
        backref=db.backref("lotes_receta", lazy="dynamic"),
    )


class LoteInsumo(db.Model):
    __tablename__ = "lotes_insumo"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    precio_unidad = db.Column(db.Float, nullable=False)
    merma = db.Column(db.Float, nullable=False, default=0)

    idInsumo = db.Column(db.Integer, db.ForeignKey("insumos.id"), nullable=False)
    idCompra = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)

    compra = db.relationship(
        "Compra",
        foreign_keys=[idCompra],
        back_populates="lotes_insumo_compra",
    )
    insumo = db.relationship(
        "Insumo",
        foreign_keys=[idInsumo],
        backref=db.backref("lotes_insumo", lazy="dynamic"),
    )


class SolicitudProduccion(db.Model):
    __tablename__ = "solicitudes_produccion"

    id = db.Column(db.Integer, primary_key=True)

    fecha_produccion = db.Column(db.Date)
    mensaje = db.Column(db.String(50))
    estatus = db.Column(db.Integer, nullable=False)
    tandas = db.Column(db.Integer)
    merma = db.Column(db.Integer)
    fecha_solicitud = db.Column(db.Date, nullable=False)

    fecha_solicitud = db.Column(db.DateTime, default=datetime.now)
    fecha_produccion = db.Column(db.Date)

    posicion = db.Column(db.Integer, default=1)
    idReceta = db.Column(db.Integer, db.ForeignKey("recetas.id"), nullable=False)

    idUsuarioSolicitud = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False
    )
    idUsuarioProduccion = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False
    )

    receta = db.relationship(
        "Receta", backref=db.backref("solicitudes_produccion", lazy="dynamic")
    )

    usuarioSolicitud = db.relationship(
        "Usuario",
        foreign_keys=[idUsuarioSolicitud],
        backref=db.backref("solicitudes_produccion_vendedor", lazy="dynamic"),
    )
    usuarioProduccion = db.relationship(
        "Usuario",
        foreign_keys=[idUsuarioProduccion],
        backref=db.backref("solicitudes_produccion_cocinero", lazy="dynamic"),
    )

    @staticmethod
    def get_next_position():
        # Obtiene la siguiente posición disponible
        max_position = db.session.query(func.max(SolicitudProduccion.posicion)).scalar()
        return (max_position or 0) + 1

    def __init__(self, *args, **kwargs):
        super(SolicitudProduccion, self).__init__(*args, **kwargs)
        if (
            self.posicion is None
        ):  # Si no se proporciona una posición, asigna la siguiente disponible
            self.posicion = self.get_next_position()


class TransaccionCaja(db.Model):
    __tablename__ = "transacciones_caja"

    id = db.Column(db.Integer, primary_key=True)
    monto_egreso = db.Column(db.Float)
    monto_ingreso = db.Column(db.Float)
    fecha_transaccion = db.Column(db.Date)

    idCorteCaja = db.Column(db.Integer, db.ForeignKey("cortes_caja.id"), nullable=False)
