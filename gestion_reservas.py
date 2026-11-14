
# PARTE 3: GESTIÓN DE RESERVAS Y PRUEBAS
# Desarrollado por: Jesus Escorcia Pino


from excepciones_y_clases_bases import DatoInvalidoError, ServicioNoDisponibleError, ReservaError
from clientes_servicios import Cliente, Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from datetime import date, datetime
import logging

MAX_DIAS_ANTICIPACION = 365


def validar_fecha(valor):
    """Convierte 'AAAA-MM-DD' (o un objeto date) en date, validando que no sea pasada
    ni esté a más de un año de anticipación."""
    if isinstance(valor, date):
        fecha = valor
    else:
        try:
            fecha = datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
        except ValueError:
            logging.error(f"Fecha inválida: {valor!r}")
            raise DatoInvalidoError("La fecha debe tener el formato AAAA-MM-DD (ej. 2026-12-01).") from None
    hoy = date.today()
    if fecha < hoy:
        logging.error(f"Fecha en el pasado: {fecha}")
        raise DatoInvalidoError("No se pueden hacer reservas en fechas pasadas.")
    if (fecha - hoy).days > MAX_DIAS_ANTICIPACION:
        logging.error(f"Fecha demasiado lejana: {fecha}")
        raise DatoInvalidoError(f"Solo se puede reservar con máximo {MAX_DIAS_ANTICIPACION} días de anticipación.")
    return fecha


class Reserva:
    """Controla el flujo completo de una reserva aplicando bloques try/except/else/finally y logging."""
    _contador = 100

    def __init__(self, cliente, servicio, tiempo, fecha=None):
        Reserva._contador += 1
        self.id_reserva = f"RES-{Reserva._contador}"
        self.cliente = cliente
        self.servicio = servicio
        self.tiempo = tiempo
        self.fecha = validar_fecha(fecha) if fecha is not None else None
        self.estado = "Pendiente"
        self.costo_total = 0.0
        self.parametros = {}

    def procesar(self, *args, **kwargs):
        """Procesa la reserva de manera robusta controlando errores y registrando estados."""
        logging.info(f"Intentando procesar la reserva {self.id_reserva}")
        if self.estado != "Pendiente":
            raise ReservaError(f"La reserva {self.id_reserva} ya fue procesada (estado: {self.estado}).")
        self.parametros = dict(kwargs)
        try:
            # Validación de tipos de datos en la reserva
            if not isinstance(self.cliente, Cliente) or not isinstance(self.servicio, Servicio):
                raise ReservaError("Datos de cliente o servicio incorrectos.")

            # Control de disponibilidad: servicio activo y fecha libre
            self.servicio.verificar_disponibilidad(self.fecha)

            # Cálculo polimórfico del costo del servicio
            self.costo_total = self.servicio.calcular_costo(*args, **kwargs)

            # Se bloquea la fecha para que nadie más pueda reservar el servicio ese día
            if self.fecha is not None:
                self.servicio.ocupar(self.fecha)

        except (DatoInvalidoError, ServicioNoDisponibleError) as e:
            # Captura de errores controlados específicos
            logging.warning(f"Error controlado en reserva {self.id_reserva}: {e}")
            self.estado = "Fallida"
            raise ReservaError(f"No se pudo completar la reserva {self.id_reserva}") from e
        
        except Exception as ex:
            # Captura de errores críticos inesperados con encadenamiento
            logging.critical(f"Error inesperado en reserva {self.id_reserva}: {ex}")
            self.estado = "Error"
            raise ReservaError("Ocurrió un error grave en el sistema.") from ex
        
        else:
            # Se ejecuta únicamente si no ocurre ninguna excepción
            self.estado = "Confirmada"
            logging.info(f"Reserva {self.id_reserva} confirmada con éxito. Total: {self.costo_total}")
        
        finally:
            # Se ejecuta siempre, garantizando registro del estado final
            logging.info(f"Finalizó el proceso de la reserva {self.id_reserva}. Estado actual: {self.estado}")

    def cancelar(self):
        """Permite cancelar únicamente reservas que se encuentren confirmadas."""
        if self.estado == "Confirmada":
            self.estado = "Cancelada"
            if self.fecha is not None:
                self.servicio.liberar(self.fecha)  # La fecha vuelve a quedar disponible
            logging.info(f"Reserva {self.id_reserva} cancelada.")
        else:
            raise ReservaError("Solo se pueden cancelar reservas que estén confirmadas.")


def correr_pruebas():
    """Función que ejecuta las 11 operaciones requeridas por la guía (exitosas y fallidas)."""
    print("=== INICIANDO PRUEBAS DEL SISTEMA ===")
    clientes = []
    servicios = []
    reservas = []

    # 1. Registro correcto de cliente
    try:
        c1 = Cliente("C1", "Carlos Pérez", "carlos@mail.com")
        clientes.append(c1)
        print("1. Éxito:", c1.mostrar_info())
    except Exception as e:
        print("1. Error:", e)

    # 2. Registro inválido de cliente (nombre corto) -> Genera DatoInvalidoError
    try:
        c2 = Cliente("C2", "Jo", "jo@mail.com")
    except DatoInvalidoError as e:
        print("2. Excepción controlada (nombre corto):", e)

    # 3. Creación correcta de sala
    try:
        s1 = ReservaSala("S1", "Sala Magna", 50000, 30)
        servicios.append(s1)
        print("3. Éxito:", s1.mostrar_info())
    except Exception as e:
        print("3. Error:", e)

    # 4. Creación incorrecta de servicio (costo negativo) -> Genera DatoInvalidoError
    try:
        s_malo = ReservaSala("S2", "Sala Chica", -5000, 5)
    except DatoInvalidoError as e:
        print("4. Excepción controlada (costo negativo):", e)

    # 5. Creación correcta de equipo
    try:
        e1 = AlquilerEquipo("E1", "Proyector Epson", 40000, "Epson")
        servicios.append(e1)
        print("5. Éxito:", e1.mostrar_info())
    except Exception as e:
        print("5. Error:", e)

    # 6. Creación correcta de asesoría
    try:
        a1 = AsesoriaEspecializada("A1", "Base de Datos", 70000, "SQL")
        servicios.append(a1)
        print("6. Éxito:", a1.mostrar_info())
    except Exception as e:
        print("6. Error:", e)

    # 7. Reserva exitosa con sobrecarga de parámetros (horas, impuesto, descuento)
    try:
        r1 = Reserva(clientes[0], servicios[0], 3)
        r1.procesar(horas=3, impuesto=True, descuento=10.0)
        reservas.append(r1)
        print(f"7. Éxito: Reserva {r1.id_reserva} creada por ${r1.costo_total}")
    except Exception as e:
        print("7. Error:", e)

    # 8. Reserva fallida por servicio no disponible -> Genera ServicioNoDisponibleError
    try:
        servicios[1].disponible = False  # Apagamos el equipo
        r2 = Reserva(clientes[0], servicios[1], 2)
        r2.procesar(dias=2, seguro=True)
    except ReservaError as e:
        print("8. Excepción controlada (servicio no disponible):", e)

    # 9. Reserva de asesoría presencial (con costo extra)
    try:
        r3 = Reserva(clientes[0], servicios[2], 2)
        r3.procesar(sesiones=2, virtual=False)
        reservas.append(r3)
        print(f"9. Éxito: Reserva {r3.id_reserva} creada por ${r3.costo_total}")
    except Exception as e:
        print("9. Error:", e)

    # 10. Cancelar una reserva confirmada
    try:
        reservas[0].cancelar()
        print(f"10. Éxito: Reserva {reservas[0].id_reserva} cancelada correctamente.")
    except Exception as e:
        print("10. Error:", e)

    # 11. Intentar cancelar una reserva que ya fue cancelada -> Genera ReservaError
    try:
        reservas[0].cancelar()
    except ReservaError as e:
        print("11. Excepción controlada (operación no permitida):", e)

    print("=== PRUEBAS FINALIZADAS CON ÉXITO ===")

if __name__ == "__main__":
    correr_pruebas()