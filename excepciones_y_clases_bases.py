
# Parte 1: EXCEPCIONES Y CLASES BASE
# Desarrollado por: Yorman Orozco Villa


import logging
from abc import ABC, abstractmethod

# Configuración básica para guardar los errores en un archivo log externo (sistema.log)
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Jerarquía de excepciones personalizadas para Software FJ
class SoftwareFJError(Exception):
    """Clase base para todas las excepciones del sistema."""
    pass

class DatoInvalidoError(SoftwareFJError):
    """Se arroja cuando un dato ingresado no cumple con las validaciones (ej. nombres cortos, costos negativos)."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Se arroja al intentar reservar un servicio que se encuentra inactivo o no disponible."""
    pass

class ReservaError(SoftwareFJError):
    """Se arroja cuando ocurre un fallo general o una operación no permitida durante el proceso de reserva."""
    pass

# Clase abstracta principal que heredan las entidades del sistema
class Entidad(ABC):
    """Clase abstracta que define la estructura base para objetos con identificación única."""
    
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self):
        """Devuelve el identificador único de la entidad."""
        return self._id_entidad

    @abstractmethod
    def mostrar_info(self):
        """Método abstracto obligatorio para mostrar información detallada de la entidad."""
        pass