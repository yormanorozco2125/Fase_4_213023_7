
# PARTE 4: GESTOR INTEGRAL DEL SISTEMA
# Centraliza la administración dinámica de clientes, servicios y reservas.
# Es utilizado por la interfaz gráfica (interfaz_grafica.py).


import logging
from datetime import date, timedelta

from excepciones_y_clases_bases import DatoInvalidoError, ReservaError
from clientes_servicios import Cliente, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestion_reservas import Reserva, validar_fecha


class SistemaGestion:
    """Administra en memoria los clientes, servicios y reservas de Software FJ."""

    # Tipo de servicio -> (clase, prefijo del ID, nombre del atributo especial)
    TIPOS_SERVICIO = {
        "Sala": (ReservaSala, "SAL", "capacidad"),
        "Equipo": (AlquilerEquipo, "EQU", "marca"),
        "Asesoría": (AsesoriaEspecializada, "ASE", "area"),
    }

    def __init__(self):
        self.clientes = {}
        self.servicios = {}
        self.reservas = {}
        self._consecutivos = {}

    # ------------------------------------------------------------------ util
    def _nuevo_id(self, prefijo):
        self._consecutivos[prefijo] = self._consecutivos.get(prefijo, 0) + 1
        return f"{prefijo}-{self._consecutivos[prefijo]:03d}"

    def obtener_cliente(self, id_cliente):
        try:
            return self.clientes[id_cliente]
        except KeyError:
            raise DatoInvalidoError(f"No existe un cliente con ID '{id_cliente}'.") from None

    def obtener_servicio(self, id_servicio):
        try:
            return self.servicios[id_servicio]
        except KeyError:
            raise DatoInvalidoError(f"No existe un servicio con ID '{id_servicio}'.") from None

    def obtener_reserva(self, id_reserva):
        try:
            return self.reservas[id_reserva]
        except KeyError:
            raise DatoInvalidoError(f"No existe la reserva '{id_reserva}'.") from None

    # -------------------------------------------------------------- clientes
    def registrar_cliente(self, nombre, correo):
        """Crea un cliente validado; no permite correos repetidos."""
        correo_normalizado = (correo or "").strip().lower()
        if any(c.correo == correo_normalizado for c in self.clientes.values()):
            logging.error(f"Correo duplicado: {correo_normalizado}")
            raise DatoInvalidoError(f"Ya existe un cliente registrado con el correo {correo_normalizado}.")
        cliente = Cliente(self._nuevo_id("CLI"), nombre, correo)
        self.clientes[cliente.id_entidad] = cliente
        logging.info(f"Cliente registrado: {cliente.mostrar_info()}")
        return cliente

    def reservas_activas_de_cliente(self, id_cliente):
        return [r for r in self.reservas.values()
                if r.cliente.id_entidad == id_cliente and r.estado == "Confirmada"]

    def eliminar_cliente(self, id_cliente):
        """Elimina un cliente solo si no tiene reservas confirmadas."""
        cliente = self.obtener_cliente(id_cliente)
        if self.reservas_activas_de_cliente(id_cliente):
            raise ReservaError(f"{cliente.nombre} tiene reservas confirmadas; cancélelas antes de eliminarlo.")
        del self.clientes[id_cliente]
        logging.info(f"Cliente eliminado: {id_cliente}")

    # ------------------------------------------------------------- servicios
    def registrar_servicio(self, tipo, nombre, costo_base, atributo_especial):
        """Crea un servicio del tipo indicado (Sala, Equipo o Asesoría)."""
        if tipo not in self.TIPOS_SERVICIO:
            raise DatoInvalidoError(f"Tipo de servicio desconocido: {tipo}.")
        clase, prefijo, _ = self.TIPOS_SERVICIO[tipo]
        nombre_normalizado = (nombre or "").strip().lower()
        if any(s.nombre.lower() == nombre_normalizado and s.TIPO == tipo for s in self.servicios.values()):
            logging.error(f"Servicio duplicado: {tipo} {nombre}")
            raise DatoInvalidoError(f"Ya existe un servicio de tipo {tipo} llamado '{nombre.strip()}'.")
        servicio = clase(self._nuevo_id(prefijo), nombre, costo_base, atributo_especial)
        self.servicios[servicio.id_entidad] = servicio
        logging.info(f"Servicio registrado: {servicio.mostrar_info()}")
        return servicio

    def cambiar_disponibilidad(self, id_servicio):
        """Activa / desactiva un servicio (p. ej. por mantenimiento)."""
        servicio = self.obtener_servicio(id_servicio)
        servicio.disponible = not servicio.disponible
        return servicio.disponible

    # -------------------------------------------------------------- reservas
    @staticmethod
    def _tiempo_de(parametros):
        for clave in ("horas", "dias", "sesiones"):
            if clave in parametros:
                return parametros[clave]
        return 1

    def cotizar(self, id_servicio, fecha, **parametros):
        """Calcula el costo sin crear la reserva, verificando disponibilidad en la fecha."""
        servicio = self.obtener_servicio(id_servicio)
        servicio.verificar_disponibilidad(validar_fecha(fecha))
        return servicio.calcular_costo(**parametros)

    def crear_reserva(self, id_cliente, id_servicio, fecha, **parametros):
        """Crea y procesa una reserva. Se guarda en el historial aunque falle."""
        cliente = self.obtener_cliente(id_cliente)
        servicio = self.obtener_servicio(id_servicio)
        reserva = Reserva(cliente, servicio, self._tiempo_de(parametros), fecha=fecha)
        self.reservas[reserva.id_reserva] = reserva
        reserva.procesar(**parametros)  # Lanza ReservaError si falla (estado "Fallida")
        return reserva

    def cancelar_reserva(self, id_reserva):
        self.obtener_reserva(id_reserva).cancelar()

    @staticmethod
    def describir_parametros(reserva):
        p = reserva.parametros
        partes = []
        if "horas" in p:
            partes.append(f"{p['horas']} h")
        if p.get("asistentes"):
            partes.append(f"{p['asistentes']} pers.")
        if p.get("descuento"):
            partes.append(f"desc. {p['descuento']}%")
        if "impuesto" in p:
            partes.append("con IVA" if p["impuesto"] else "sin IVA")
        if "dias" in p:
            partes.append(f"{p['dias']} día(s)")
        if "seguro" in p:
            partes.append("con seguro" if p["seguro"] else "sin seguro")
        if "sesiones" in p:
            partes.append(f"{p['sesiones']} sesión(es)")
        if "virtual" in p:
            partes.append("virtual" if p["virtual"] else "presencial")
        return ", ".join(partes)

    # --------------------------------------------------------- datos demo
    def cargar_datos_ejemplo(self):
        """Carga algunos registros de ejemplo para probar rápidamente la aplicación."""
        manana = date.today() + timedelta(days=1)
        c1 = self.registrar_cliente("Carlos Pérez", "carlos@mail.com")
        self.registrar_cliente("Ana Gómez", "ana.gomez@mail.com")
        s1 = self.registrar_servicio("Sala", "Sala Magna", 50000, 30)
        self.registrar_servicio("Sala", "Sala Juntas", 30000, 10)
        self.registrar_servicio("Equipo", "Proyector Epson", 40000, "Epson")
        self.registrar_servicio("Asesoría", "Base de Datos", 70000, "SQL")
        self.crear_reserva(c1.id_entidad, s1.id_entidad, manana,
                           horas=3, impuesto=True, descuento=10.0, asistentes=20)
