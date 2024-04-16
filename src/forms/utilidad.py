""" FORMULARIOS DE UTILIDADES """

from wtforms import FloatField, Form, SelectField, SubmitField, validators


class UtilidadForm(Form):
    """CLASE QUE DEFINE EL FORMULARIO DE LA UTILIDAD DE LAS RECETAS"""

    receta = SelectField(
        "Receta",
        [
            validators.DataRequired(message="El Campo es Requerido"),
        ],
        choices=[],
    )
    porcentaje = FloatField(
        "Porcentaje",
        [
            validators.DataRequired(message="El campo es Requerido"),
            validators.NumberRange(
                min=0, max=100, message="Ingresa un Porcentaje Válido"
            ),
        ],
    )
    cantidad = FloatField(
        "Cantidad",
        [
            validators.DataRequired(message="El Campo es Requerido"),
            validators.NumberRange(min=1, message="Ingresa una Cantidad Válida"),
        ],
    )
    submit = SubmitField("GUARDAR")
