""""""

from wtforms import (
    Form,
    StringField,
    IntegerField,
    FloatField,
    DateField,
    SelectField,
    SubmitField,
    validators,
)


class CompraForm(Form):
    """Clase que define el formulario de compra"""

    proveedor = SelectField(
        "Proveedor",
        [validators.DataRequired(message="Selecciona un proveedor")],
        choices=[],
    )
    fecha_compra = DateField("Fecha de Compra", format="%Y-%m-%d")
    total = FloatField(
        "Total", [validators.DataRequired(message="Ingresa el total de la compra")]
    )
    submit = SubmitField("Guardar")
