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
    cantidad = FloatField(
        "Cantidad",
        [
            validators.DataRequired(message="El Campo es Requerido"),
            validators.NumberRange(min=1, message="Ingresa una Cantidad Válida"),
        ],
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
