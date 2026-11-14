
# PARTE 2: CLIENTES Y SERVICIOS ESPECIALIZADOS
# Desarrollado por:David Salazar Morales
# Mejoras (retroalimentación): validaciones reforzadas y control de disponibilidad por fecha.


from excepciones_y_clases_bases import Entidad, DatoInvalidoError, ServicioNoDisponibleError
from abc import ABC, abstractmethod
import logging
import re

# Patrones de validación
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)*\.[A-Za-z]{2,}$")
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' ]+$")


# ---------------------------------------------------------------------------
# Funciones auxiliares de validación (reutilizadas por todas las clases)
# ---------------------------------------------------------------------------
def validar_texto(valor, campo, minimo=3, maximo=60):
    """Valida que el valor sea un texto con longitud entre 'minimo' y 'maximo'."""
    if not isinstance(valor, str) or len(valor.strip()) < minimo:
        logging.error(f"{campo} inválido: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' debe tener al menos {minimo} caracteres.")
    valor = valor.strip()
    if len(valor) > maximo:
        logging.error(f"{campo} demasiado largo: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' no puede superar {maximo} caracteres.")
    return valor


def validar_numero(valor, campo, minimo=None, maximo=None, entero=False):
    """Valida que el valor sea numérico (no booleano) y esté dentro del rango indicado."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        logging.error(f"{campo} no numérico: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' debe ser numérico.")
    if entero and not float(valor).is_integer():
        logging.error(f"{campo} no entero: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' debe ser un número entero.")
    if minimo is not None and valor < minimo:
        logging.error(f"{campo} por debajo del mínimo: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' debe ser mayor o igual a {minimo}.")
    if maximo is not None and valor > maximo:
        logging.error(f"{campo} por encima del máximo: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' no puede ser mayor a {maximo}.")
    return int(valor) if entero else valor


def validar_booleano(valor, campo):
    """Valida que el valor sea estrictamente True o False."""
    if not isinstance(valor, bool):
        logging.error(f"{campo} no booleano: {valor!r}")
        raise DatoInvalidoError(f"El campo '{campo}' debe ser verdadero o falso.")
    return valor


# Clase Cliente con encapsulación estricta y validaciones
class Cliente(Entidad):
    """Representa a un cliente de la empresa Software FJ con validaciones en propiedades."""

    def __init__(self, id_entidad, nombre, correo):
        super().__init__(id_entidad)
        self.nombre = nombre  # Utiliza el setter validado
        self.correo = correo  # Utiliza el setter validado

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Validación estricta: mínimo 3 caracteres y solo letras/espacios
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            logging.error(f"Nombre inválido: {valor}")
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        valor = validar_texto(valor, "Nombre", minimo=3, maximo=60)
        if not PATRON_NOMBRE.match(valor):
            logging.error(f"Nombre con caracteres inválidos: {valor}")
            raise DatoInvalidoError("El nombre solo puede contener letras y espacios.")
        self._nombre = " ".join(valor.split())

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        # Validación estricta: formato usuario@dominio.ext
        if not isinstance(valor, str) or not PATRON_CORREO.match(valor.strip()):
            logging.error(f"Correo inválido: {valor}")
            raise DatoInvalidoError("El correo electrónico no es válido.")
        self._correo = valor.strip().lower()

    def mostrar_info(self):
        return f"Cliente: {self.nombre} (ID: {self.id_entidad})"


# Clase abstracta Servicio
class Servicio(Entidad, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    TIPO = "Servicio"

    def __init__(self, id_entidad, nombre, costo_base, disponible=True):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = disponible
        # Control de disponibilidad: fechas que ya tienen una reserva confirmada
        self._fechas_reservadas = set()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = validar_texto(valor, "Nombre del servicio", minimo=3, maximo=60)

    @property
    def costo_base(self):
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            logging.error(f"Costo base no numérico: {valor!r}")
            raise DatoInvalidoError("El costo base debe ser numérico.")
        if valor < 0:
            logging.error(f"Costo base negativo: {valor}")
            raise DatoInvalidoError("El costo base no puede ser negativo.")
        if valor == 0:
            logging.error("Costo base en cero")
            raise DatoInvalidoError("El costo base debe ser mayor a cero.")
        self._costo_base = float(valor)

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = validar_booleano(valor, "Disponible")
        logging.info(f"Servicio {self.id_entidad} -> disponible={self._disponible}")

    @property
    def fechas_reservadas(self):
        """Devuelve una copia ordenada de las fechas ocupadas (solo lectura)."""
        return sorted(self._fechas_reservadas)

    # --- Control de disponibilidad ---------------------------------------
    def verificar_disponibilidad(self, fecha=None):
        """Lanza ServicioNoDisponibleError si el servicio está inactivo u ocupado en la fecha."""
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' está fuera de servicio.")
        if fecha is not None and fecha in self._fechas_reservadas:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' ya está reservado para el {fecha}.")

    def ocupar(self, fecha):
        """Marca una fecha como reservada para este servicio."""
        self.verificar_disponibilidad(fecha)
        self._fechas_reservadas.add(fecha)

    def liberar(self, fecha):
        """Libera una fecha previamente reservada (por ejemplo, al cancelar)."""
        self._fechas_reservadas.discard(fecha)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Método polimórfico para calcular costos según el tipo de servicio."""
        pass

    @abstractmethod
    def detalle(self):
        """Dato característico de cada servicio (capacidad, marca o área)."""
        pass


# 1. Servicio especializado: Salas
class ReservaSala(Servicio):
    """Gestión de reservas de salas físicas con cálculo por horas, impuestos y descuentos."""

    TIPO = "Sala"
    MAX_HORAS = 12

    def __init__(self, id_entidad, nombre, costo_base, capacidad, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.capacidad = capacidad

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        self._capacidad = validar_numero(valor, "Capacidad", minimo=1, maximo=500, entero=True)

    def calcular_costo(self, horas=1, impuesto=True, descuento=0.0, asistentes=None):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La sala {self.nombre} no está disponible.")
        if isinstance(horas, (int, float)) and not isinstance(horas, bool) and horas <= 0:
            raise DatoInvalidoError("Las horas deben ser mayores a cero.")
        horas = validar_numero(horas, "Horas", minimo=0.5, maximo=self.MAX_HORAS)
        descuento = validar_numero(descuento, "Descuento (%)", minimo=0, maximo=100)
        validar_booleano(impuesto, "Impuesto")
        if asistentes is not None:
            asistentes = validar_numero(asistentes, "Asistentes", minimo=1, entero=True)
            if asistentes > self.capacidad:
                raise ServicioNoDisponibleError(
                    f"La sala {self.nombre} tiene capacidad para {self.capacidad} "
                    f"personas y se solicitaron {asistentes}.")

        subtotal = self.costo_base * horas
        if descuento > 0:
            subtotal -= subtotal * (descuento / 100)
        if impuesto:
            subtotal *= 1.19  # Aplicación del 19% de IVA
        return round(subtotal, 2)

    def detalle(self):
        return f"Capacidad: {self.capacidad} personas"

    def mostrar_info(self):
        return f"Sala: {self.nombre} | Capacidad: {self.capacidad} | Costo/h: {self.costo_base}"


# 2. Servicio especializado: Alquiler de Equipos
class AlquilerEquipo(Servicio):
    """Gestión de alquiler de equipos tecnológicos por días con opción de seguro."""

    TIPO = "Equipo"
    MAX_DIAS = 30
    SEGURO_DIARIO = 15000

    def __init__(self, id_entidad, nombre, costo_base, marca, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.marca = marca

    @property
    def marca(self):
        return self._marca

    @marca.setter
    def marca(self, valor):
        self._marca = validar_texto(valor, "Marca", minimo=2, maximo=40)

    def calcular_costo(self, dias=1, seguro=False):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El equipo {self.nombre} no está disponible.")
        if isinstance(dias, (int, float)) and not isinstance(dias, bool) and dias <= 0:
            raise DatoInvalidoError("Los días deben ser mayores a cero.")
        dias = validar_numero(dias, "Días", minimo=1, maximo=self.MAX_DIAS, entero=True)
        validar_booleano(seguro, "Seguro")

        total = self.costo_base * dias
        if seguro:
            total += self.SEGURO_DIARIO * dias  # Costo fijo de seguro diario
        return round(total, 2)

    def detalle(self):
        return f"Marca: {self.marca}"

    def mostrar_info(self):
        return f"Equipo: {self.nombre} ({self.marca}) | Costo/día: {self.costo_base}"


# 3. Servicio especializado: Asesorías
class AsesoriaEspecializada(Servicio):
    """Gestión de asesorías profesionales virtuales o presenciales."""

    TIPO = "Asesoría"
    MAX_SESIONES = 20
    RECARGO_PRESENCIAL = 50000

    def __init__(self, id_entidad, nombre, costo_base, area, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.area = area

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self, valor):
        self._area = validar_texto(valor, "Área", minimo=2, maximo=40)

    def calcular_costo(self, sesiones=1, virtual=True):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La asesoría {self.nombre} no está disponible.")
        if isinstance(sesiones, (int, float)) and not isinstance(sesiones, bool) and sesiones <= 0:
            raise DatoInvalidoError("Las sesiones deben ser mayores a cero.")
        sesiones = validar_numero(sesiones, "Sesiones", minimo=1, maximo=self.MAX_SESIONES, entero=True)
        validar_booleano(virtual, "Virtual")

        total = self.costo_base * sesiones
        if not virtual:
            total += self.RECARGO_PRESENCIAL  # Recargo por asesoría presencial
        return round(total, 2)

    def detalle(self):
        return f"Área: {self.area}"

    def mostrar_info(self):
        return f"Asesoría: {self.nombre} ({self.area}) | Costo/sesión: {self.costo_base}"
