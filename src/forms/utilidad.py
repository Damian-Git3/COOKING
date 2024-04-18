""" FORMULARIOS DE UTILIDADES """

from gc import disable
from math import cos

from click import style
from sqlalchemy import Integer
from wtforms import FloatField, Form, IntegerField, SelectField, SubmitField, validators

from database.models import Receta


class GetRecetaForm(Form):
    """CLASE QUE DEFINE EL FORMULARIO DE LA UTILIDAD DE LAS RECETAS"""

    receta = SelectField(
        "Receta",
        [
            validators.DataRequired(message="El Campo es Requerido"),
        ],
        choices=[],
    )
    submit = SubmitField("GUARDAR")

    def __str__(self):
        """Devuelve una representación en cadena de texto de los datos del formulario."""
        # Inicializa una cadena de texto vacía para almacenar la representación
        form_representation = ""

        # Recorre cada campo del formulario
        for field_name, field in self._fields.items():
            # Añade el nombre del campo y su valor al string
            form_representation += f"{field_name}: {field.data}, "

            # Añade los mensajes de error o validación si existen
            if field.errors:
                form_representation += f"Errores: {', '.join(field.errors)}, "

        # Elimina la última coma y espacio
        form_representation = form_representation.rstrip(", ")

        return form_representation

    def __init__(self, *args, **kwargs):
        super(GetRecetaForm, self).__init__(*args, **kwargs)
        # Consultar la base de datos para obtener las recetas
        self.receta.choices = [
            (receta.id, receta.nombre) for receta in Receta.query.all()
        ]


class UtilidadForm(Form):
    """Formulario para calcular la utilidad de una receta"""

    id_receta = IntegerField(
        "ID Receta",
        render_kw={"style": "display: none"},
        validators=[
            validators.DataRequired(message="El Campo es Requerido"),
            validators.NumberRange(min=1, message="Ingresa un ID Válido"),
        ],
    )
    costo_total = FloatField("Costo Total", render_kw={"disabled": True})
    costo_venta = FloatField(
        "Costo de Venta",
        [
            validators.DataRequired(message="El Campo es Requerido"),
            validators.NumberRange(min=1, message="Ingresa un Costo Válido"),
        ],
    )
    submit = SubmitField("CALCULAR")
