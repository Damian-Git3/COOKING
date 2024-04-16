""" Este módulo contiene la definición del logger del sistema. """

import logging

import colorlog

# Crea un logger
logger = colorlog.getLogger(__name__)

# Configura el nivel de log
logger.setLevel(logging.DEBUG)

# Crea un manejador que envía los mensajes a la consola
console_handler = colorlog.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Crea un formateador con colores y lo asigna al manejador
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)
console_handler.setFormatter(formatter)

# Añade el manejador al logger
logger.addHandler(console_handler)
