""" FORMULARIOS DE UTILIDADES """

from wtforms import (FloatField, Form, IntegerField, SelectField, SubmitField,
                     validators)


class UtilidadForm(Form):
    """CLASE QUE DEFINE EL FORMULARIO DE LA UTILIDAD DE LAS RECETAS"""

    receta = SelectField(
        "Receta",
        [
            validators.DataRequired(message="el campo es requerido"),
        ],
        choices=[],
    )
    porcentaje = FloatField(
        "Porcentaje",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.NumberRange(
                min=0, max=100, message="ingresa un porcentaje válido"
            ),
        ],
    )
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.NumberRange(min=1, message="ingresa una cantidad válida"),
        ],
    )
    submit = SubmitField("Guardar")
