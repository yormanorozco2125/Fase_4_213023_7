
# PARTE 2: CLIENTES Y SERVICIOS ESPECIALIZADOS
# Desarrollado por:David Salazar Morales


from excepciones_y_clases_bases import Entidad, DatoInvalidoError, ServicioNoDisponibleError
from abc import ABC, abstractmethod
import logging

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
        # Validación estricta: el nombre debe tener al menos 3 caracteres
        if not valor or len(valor.strip()) < 3:
            logging.error(f"Nombre inválido: {valor}")
            raise DatoInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        # Validación estricta: formato básico de correo electrónico
        if not valor or "@" not in valor or "." not in valor:
            logging.error(f"Correo inválido: {valor}")
            raise DatoInvalidoError("El correo electrónico no es válido.")
        self._correo = valor.strip()

    def mostrar_info(self):
        return f"Cliente: {self.nombre} (ID: {self.id_entidad})"


# Clase abstracta Servicio
class Servicio(Entidad, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""
    
    def __init__(self, id_entidad, nombre, costo_base, disponible=True):
        super().__init__(id_entidad)
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = disponible

    @property
    def costo_base(self):
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor):
        if valor < 0:
            logging.error(f"Costo base negativo: {valor}")
            raise DatoInvalidoError("El costo base no puede ser negativo.")
        self._costo_base = float(valor)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Método polimórfico para calcular costos según el tipo de servicio."""
        pass


# 1. Servicio especializado: Salas
class ReservaSala(Servicio):
    """Gestión de reservas de salas físicas con cálculo por horas, impuestos y descuentos."""
    
    def __init__(self, id_entidad, nombre, costo_base, capacidad, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.capacidad = capacidad

    def calcular_costo(self, horas=1, impuesto=True, descuento=0.0):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La sala {self.nombre} no está disponible.")
        if horas <= 0:
            raise DatoInvalidoError("Las horas deben ser mayores a cero.")
        
        subtotal = self.costo_base * horas
        if descuento > 0:
            subtotal -= subtotal * (descuento / 100)
        if impuesto:
            subtotal *= 1.19  # Aplicación del 19% de IVA
        return round(subtotal, 2)

    def mostrar_info(self):
        return f"Sala: {self.nombre} | Capacidad: {self.capacidad} | Costo/h: {self.costo_base}"


# 2. Servicio especializado: Alquiler de Equipos
class AlquilerEquipo(Servicio):
    """Gestión de alquiler de equipos tecnológicos por días con opción de seguro."""
    
    def __init__(self, id_entidad, nombre, costo_base, marca, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.marca = marca

    def calcular_costo(self, dias=1, seguro=False):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El equipo {self.nombre} no está disponible.")
        if dias <= 0:
            raise DatoInvalidoError("Los días deben ser mayores a cero.")
        
        total = self.costo_base * dias
        if seguro:
            total += 15000 * dias  # Costo fijo de seguro diario
        return round(total, 2)

    def mostrar_info(self):
        return f"Equipo: {self.nombre} ({self.marca}) | Costo/día: {self.costo_base}"


# 3. Servicio especializado: Asesorías
class AsesoriaEspecializada(Servicio):
    """Gestión de asesorías profesionales virtuales o presenciales."""
    
    def __init__(self, id_entidad, nombre, costo_base, area, disponible=True):
        super().__init__(id_entidad, nombre, costo_base, disponible)
        self.area = area

    def calcular_costo(self, sesiones=1, virtual=True):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"La asesoría {self.nombre} no está disponible.")
        if sesiones <= 0:
            raise DatoInvalidoError("Las sesiones deben ser mayores a cero.")
        
        total = self.costo_base * sesiones
        if not virtual:
            total += 50000  # Recargo por asesoría presencial
        return round(total, 2)

    def mostrar_info(self):
        return f"Asesoría: {self.nombre} ({self.area}) | Costo/sesión: {self.costo_base}"