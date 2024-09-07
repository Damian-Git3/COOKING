from datetime import datetime

from flask import flash
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    FieldList,
    Form,
    FormField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)
from wtforms.validators import DataRequired

from database.models import CorteCaja, db


class SignupForm(Form):
    nombre = StringField(
        "nombre",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Length(min=4, max=10, message="ingresa nombre valido"),
        ],
    )
    contrasenia = PasswordField(
        "Contraseña",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.EqualTo("confirmacion", message="las contraseñas no coinciden"),
        ],
    )
    confirmacion = PasswordField("Confirmar Contraseña")
    correo = StringField(
        "Correo",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.Email(message="ingresa un correo electrónico válido"),
        ],
    )


class SolicitudProduccionForm(Form):

    receta = SelectField(
        "Receta", [validators.DataRequired(message="Selecciona una receta")], choices=[]
    )
    tandas = IntegerField(
        "Número de Tandas",
        [
            validators.DataRequired(message="Ingresa el número de tandas"),
            validators.NumberRange(
                min=1, message="El número de tandas debe ser mayor a 0"
            ),
        ],
    )
    fecha_solicitud = DateField(
        "Fecha de Solicitud", default=datetime.today(), format="%Y-%m-%d"
    )


class ModificarSolicitudProduccionForm(Form):

    tandas = IntegerField(
        "Número de Tandas",
        [
            validators.DataRequired(message="Ingresa el número de tandas"),
            validators.NumberRange(
                min=1, message="El número de tandas debe ser mayor a 0"
            ),
        ],
    )
    fecha_solicitud = DateField(
        "Fecha de Solicitud", default=datetime.today(), format="%Y-%m-%d"
    )
    mensaje = TextAreaField("Mensaje")


class BusquedaLoteGalletaForm(Form):
    fecha_inicio = DateField(
        "Fecha de Inicio",
        format="%Y-%m-%d",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío.")
        ],
    )
    fecha_fin = DateField(
        "Fecha de Fin",
        format="%Y-%m-%d",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío.")
        ],
    )

    # Assuming get_recetas() returns a list of tuples like [(id, name), ...]
    receta = SelectField(
        "Receta",
        choices=[],
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío.")
        ],
    )


class MermaGalletaForm(Form):
    lot_id = HiddenField("Lot ID")
    tipo_medida = SelectField(
        "Tipo de Medida",
        choices=[("g", "Gramos"), ("p", "Piezas")],
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío.")
        ],
    )
    cantidad = IntegerField(
        "Cantidad",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío."),
            validators.NumberRange(min=1, message="La cantidad debe ser mayor a 0"),
        ],
    )


class MermaInsumoForm(Form):
    lot_id = HiddenField("Lot ID")
    cantidad = DecimalField(
        "Cantidad",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacío."),
            validators.NumberRange(
                min=0.001, message="La cantidad debe ser mayor a 0.001"
            ),
        ],
    )


class BusquedaCompra(Form):
    fecha_inicio = DateField(
        "Fecha de Inicio",
        format="%Y-%m-%d",
    )
    fecha_fin = DateField(
        "Fecha de Fin",
        format="%Y-%m-%d",
    )
    usa_dinero_caja = BooleanField("Usó dinero de caja")
    insumo = SelectField(
        "Insumo",
        choices=[],
    )


class BusquedaLoteInsumoForm(Form):
    fecha_inicio = DateField("Fecha de Inicio", format="%Y-%m-%d")
    fecha_fin = DateField("Fecha de Fin", format="%Y-%m-%d")
    insumo = SelectField("Insumo", choices=[])


class LoteInsumoForm(Form):
    insumos = SelectField(
        "Insumo",
        choices=[],
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacìo.")
        ],
    )
    cantidad = DecimalField(
        "Cantidad (Kilos o Litros)",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacìo.")
        ],
    )
    fecha_caducidad = DateField(
        "Fecha de Caducidad",
        format="%Y-%m-%d",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacìo.")
        ],
    )
    costo_lote = DecimalField(
        "Costo del Lote",
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacìo.")
        ],
    )


class NuevaCompraForm(Form):
    proveedores = SelectField(
        "Proveedor",
        choices=[],
        validators=[
            validators.DataRequired(message="Este campo no puede estar vacìo.")
        ],
    )
    caja = BooleanField("¿Retirar dinero de la caja?", default=True)
    lotes_insumos = FieldList(FormField(LoteInsumoForm), min_entries=1)

    def validate(self):
        # Primero, realiza la validación estándar del formulario
        if not super().validate():
            return False

        if self.caja.data:
            # Luego, verifica si hay suficiente dinero en la caja
            caja = (
                db.session.query(CorteCaja)
                .filter(CorteCaja.fecha_corte == datetime.now().date())
                .first()
            )

            if not caja or caja.monto_final < sum(
                [lote.costo_lote.data for lote in self.lotes_insumos]
            ):
                flash(
                    "No hay suficiente dinero en la caja para realizar la compra",
                    "danger",
                )
                return False

        return True


class busquedaRecetaPuntoVenta(Form):
    buscar = StringField(
        "Buscar",
        render_kw={"placeholder": "Buscar galleta"},
    )


class agregarProductoPuntoVenta(Form):
    id = HiddenField("id")
    cantidad = IntegerField(
        "Cantidad",
        [validators.DataRequired(message="Ingresa un valor")],
        render_kw={"placeholder": "Cantidad"},
    )


class devolucionForm(Form):
    cantidad = DecimalField(
        "Cantidad",
        [validators.DataRequired(message="Ingresa un valor")],
        render_kw={"placeholder": "Escribir cantidad de devolución..."},
    )

    def validate(self):
        # Primero, realiza la validación estándar del formulario
        if not super().validate():
            return False

        # Luego, verifica si hay suficiente dinero en la caja
        caja = (
            db.session.query(CorteCaja)
            .filter(CorteCaja.fecha_corte == datetime.now().date())
            .first()
        )

        if not caja or caja.monto_final < self.cantidad.data:
            flash(
                "No hay suficiente dinero en la caja para realizar el retiro",
                "danger",
            )
            return False

        return True
