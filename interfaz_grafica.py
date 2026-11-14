
# PARTE 5: INTERFAZ GRÁFICA (Tkinter)
# Permite gestionar de forma dinámica clientes, servicios y reservas,
# mostrando al usuario los errores controlados por el sistema de excepciones.


import logging
import os
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk, messagebox

from excepciones_y_clases_bases import SoftwareFJError, DatoInvalidoError
from sistema_gestion import SistemaGestion

RUTA_LOG = os.path.join(os.getcwd(), "sistema.log")


# ---------------------------------------------------------------------------
# Conversión segura de los textos ingresados en los formularios
# ---------------------------------------------------------------------------
def a_entero(texto, campo):
    try:
        return int(str(texto).strip())
    except ValueError:
        logging.error(f"Valor no entero en {campo}: {texto!r}")
        raise DatoInvalidoError(f"'{campo}' debe ser un número entero.") from None


def a_decimal(texto, campo):
    try:
        return float(str(texto).strip().replace(",", "."))
    except ValueError:
        logging.error(f"Valor no numérico en {campo}: {texto!r}")
        raise DatoInvalidoError(f"'{campo}' debe ser un número.") from None


def texto_error(error):
    """Mensaje legible que incluye la causa original (excepciones encadenadas)."""
    mensaje = str(error)
    if error.__cause__ is not None:
        mensaje += f"\n\nMotivo: {error.__cause__}"
    return mensaje


def moneda(valor):
    return f"${valor:,.0f}".replace(",", ".")


def id_de(seleccion):
    """Extrae el ID de un texto de combobox con formato 'ID | descripción'."""
    return seleccion.split(" | ")[0].strip() if seleccion else ""


class AplicacionSoftwareFJ(tk.Tk):
    """Ventana principal con pestañas para Clientes, Servicios, Reservas y Log."""

    def __init__(self):
        super().__init__()
        self.sistema = SistemaGestion()
        self.title("Software FJ - Sistema de Gestión de Reservas")
        self.geometry("1050x640")
        self.minsize(950, 580)

        self._configurar_estilos()
        self._crear_menu()

        ttk.Label(self, text="Software FJ · Gestión de Clientes, Servicios y Reservas",
                  style="Titulo.TLabel").pack(fill="x", padx=12, pady=(10, 4))

        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=10, pady=6)
        self._pestana_clientes()
        self._pestana_servicios()
        self._pestana_reservas()
        self._pestana_pruebas()

        self.estado = tk.StringVar(value="Listo.")
        ttk.Label(self, textvariable=self.estado, relief="sunken", anchor="w",
                  padding=(8, 3)).pack(fill="x", side="bottom")

    # ------------------------------------------------------------- general
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"))
        estilo.configure("Total.TLabel", font=("Segoe UI", 12, "bold"), foreground="#1d6b2f")
        estilo.configure("Treeview", rowheight=24)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _crear_menu(self):
        barra = tk.Menu(self)
        archivo = tk.Menu(barra, tearoff=0)
        archivo.add_command(label="Cargar datos de ejemplo", command=self._cargar_ejemplo)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.destroy)
        barra.add_cascade(label="Archivo", menu=archivo)
        self.config(menu=barra)

    def _ok(self, mensaje):
        self.estado.set(mensaje)
        messagebox.showinfo("Operación exitosa", mensaje, parent=self)

    def _error(self, error, titulo="Error de validación"):
        self.estado.set(f"Error: {error}")
        messagebox.showerror(titulo, texto_error(error), parent=self)

    def _crear_tabla(self, padre, columnas):
        """Crea un Treeview con scroll. columnas = [(clave, título, ancho), ...]"""
        marco = ttk.Frame(padre)
        tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                             selectmode="browse")
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, anchor="w")
        scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return marco, tabla

    def _refrescar_todo(self):
        self._refrescar_clientes()
        self._refrescar_servicios()
        self._refrescar_reservas()
        self._refrescar_combos_reserva()

    def _cargar_ejemplo(self):
        try:
            self.sistema.cargar_datos_ejemplo()
        except SoftwareFJError as e:
            self._error(e, "No se pudieron cargar los datos")
        else:
            self._ok("Datos de ejemplo cargados.")
        finally:
            self._refrescar_todo()

    # ------------------------------------------------------------ clientes
    def _pestana_clientes(self):
        pagina = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(pagina, text="  Clientes  ")

        form = ttk.LabelFrame(pagina, text="Registrar cliente", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.var_cli_nombre = tk.StringVar()
        self.var_cli_correo = tk.StringVar()
        ttk.Label(form, text="Nombre completo:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_cli_nombre, width=30).grid(row=1, column=0, pady=(0, 8))
        ttk.Label(form, text="Correo electrónico:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_cli_correo, width=30).grid(row=3, column=0, pady=(0, 8))
        ttk.Button(form, text="Registrar cliente", command=self._registrar_cliente).grid(
            row=4, column=0, sticky="ew", pady=4)
        ttk.Label(form, text="• Nombre: mínimo 3 letras\n• Correo: usuario@dominio.com\n"
                             "• No se permiten correos repetidos",
                  foreground="#555").grid(row=5, column=0, sticky="w", pady=(12, 0))

        derecha = ttk.Frame(pagina)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla_clientes = self._crear_tabla(derecha, [
            ("id", "ID", 80), ("nombre", "Nombre", 220), ("correo", "Correo", 240),
            ("activas", "Reservas activas", 120)])
        marco.pack(fill="both", expand=True)
        ttk.Button(derecha, text="Eliminar cliente seleccionado",
                   command=self._eliminar_cliente).pack(anchor="e", pady=(8, 0))

    def _registrar_cliente(self):
        try:
            cliente = self.sistema.registrar_cliente(self.var_cli_nombre.get(), self.var_cli_correo.get())
        except SoftwareFJError as e:
            self._error(e)
        else:
            self.var_cli_nombre.set("")
            self.var_cli_correo.set("")
            self._refrescar_clientes()
            self._refrescar_combos_reserva()
            self._ok(f"Cliente registrado: {cliente.nombre} ({cliente.id_entidad})")

    def _eliminar_cliente(self):
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un cliente de la tabla.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el cliente seleccionado?", parent=self):
            return
        try:
            self.sistema.eliminar_cliente(seleccion[0])
        except SoftwareFJError as e:
            self._error(e, "Operación no permitida")
        else:
            self._refrescar_clientes()
            self._refrescar_combos_reserva()
            self.estado.set("Cliente eliminado.")

    def _refrescar_clientes(self):
        self.tabla_clientes.delete(*self.tabla_clientes.get_children())
        for c in self.sistema.clientes.values():
            activas = len(self.sistema.reservas_activas_de_cliente(c.id_entidad))
            self.tabla_clientes.insert("", "end", iid=c.id_entidad,
                                       values=(c.id_entidad, c.nombre, c.correo, activas))

    # ----------------------------------------------------------- servicios
    ETIQUETA_ESPECIAL = {"Sala": "Capacidad (personas):", "Equipo": "Marca:", "Asesoría": "Área:"}
    ETIQUETA_COSTO = {"Sala": "Costo por hora:", "Equipo": "Costo por día:", "Asesoría": "Costo por sesión:"}

    def _pestana_servicios(self):
        pagina = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(pagina, text="  Servicios  ")

        form = ttk.LabelFrame(pagina, text="Registrar servicio", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.var_srv_tipo = tk.StringVar(value="Sala")
        self.var_srv_nombre = tk.StringVar()
        self.var_srv_costo = tk.StringVar()
        self.var_srv_especial = tk.StringVar()

        ttk.Label(form, text="Tipo de servicio:").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(form, textvariable=self.var_srv_tipo, state="readonly", width=27,
                             values=list(SistemaGestion.TIPOS_SERVICIO))
        combo.grid(row=1, column=0, pady=(0, 8))
        combo.bind("<<ComboboxSelected>>", lambda _e: self._actualizar_etiquetas_servicio())

        ttk.Label(form, text="Nombre:").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_srv_nombre, width=30).grid(row=3, column=0, pady=(0, 8))
        self.lbl_srv_costo = ttk.Label(form)
        self.lbl_srv_costo.grid(row=4, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_srv_costo, width=30).grid(row=5, column=0, pady=(0, 8))
        self.lbl_srv_especial = ttk.Label(form)
        self.lbl_srv_especial.grid(row=6, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_srv_especial, width=30).grid(row=7, column=0, pady=(0, 8))
        ttk.Button(form, text="Registrar servicio", command=self._registrar_servicio).grid(
            row=8, column=0, sticky="ew", pady=4)
        self._actualizar_etiquetas_servicio()

        derecha = ttk.Frame(pagina)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla_servicios = self._crear_tabla(derecha, [
            ("id", "ID", 75), ("tipo", "Tipo", 75), ("nombre", "Nombre", 160),
            ("costo", "Costo base", 95), ("detalle", "Detalle", 170),
            ("estado", "Estado", 110), ("fechas", "Fechas ocupadas", 150)])
        marco.pack(fill="both", expand=True)
        self.tabla_servicios.tag_configure("inactivo", foreground="#b00020")
        ttk.Button(derecha, text="Activar / Desactivar servicio seleccionado",
                   command=self._cambiar_disponibilidad).pack(anchor="e", pady=(8, 0))

    def _actualizar_etiquetas_servicio(self):
        tipo = self.var_srv_tipo.get()
        self.lbl_srv_costo.config(text=self.ETIQUETA_COSTO[tipo])
        self.lbl_srv_especial.config(text=self.ETIQUETA_ESPECIAL[tipo])

    def _registrar_servicio(self):
        tipo = self.var_srv_tipo.get()
        try:
            costo = a_decimal(self.var_srv_costo.get(), "Costo base")
            especial = self.var_srv_especial.get()
            if tipo == "Sala":
                especial = a_entero(especial, "Capacidad")
            servicio = self.sistema.registrar_servicio(tipo, self.var_srv_nombre.get(), costo, especial)
        except SoftwareFJError as e:
            self._error(e)
        else:
            for var in (self.var_srv_nombre, self.var_srv_costo, self.var_srv_especial):
                var.set("")
            self._refrescar_servicios()
            self._refrescar_combos_reserva()
            self._ok(f"Servicio registrado: {servicio.mostrar_info()}")

    def _cambiar_disponibilidad(self):
        seleccion = self.tabla_servicios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un servicio de la tabla.", parent=self)
            return
        try:
            activo = self.sistema.cambiar_disponibilidad(seleccion[0])
        except SoftwareFJError as e:
            self._error(e)
        else:
            self._refrescar_servicios()
            self._refrescar_combos_reserva()
            self.estado.set(f"Servicio {seleccion[0]} {'activado' if activo else 'puesto fuera de servicio'}.")

    def _refrescar_servicios(self):
        self.tabla_servicios.delete(*self.tabla_servicios.get_children())
        for s in self.sistema.servicios.values():
            fechas = ", ".join(f.strftime("%d/%m") for f in s.fechas_reservadas) or "—"
            self.tabla_servicios.insert(
                "", "end", iid=s.id_entidad,
                values=(s.id_entidad, s.TIPO, s.nombre, moneda(s.costo_base), s.detalle(),
                        "Disponible" if s.disponible else "Fuera de servicio", fechas),
                tags=() if s.disponible else ("inactivo",))

    # ------------------------------------------------------------ reservas
    def _pestana_reservas(self):
        pagina = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(pagina, text="  Reservas  ")

        form = ttk.LabelFrame(pagina, text="Nueva reserva", padding=10)
        form.pack(side="left", fill="y", padx=(0, 10))

        self.var_res_cliente = tk.StringVar()
        self.var_res_servicio = tk.StringVar()
        self.var_res_fecha = tk.StringVar(value=(date.today() + timedelta(days=1)).isoformat())
        self.var_res_total = tk.StringVar(value="Total: —")

        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="w")
        self.combo_res_cliente = ttk.Combobox(form, textvariable=self.var_res_cliente,
                                              state="readonly", width=32)
        self.combo_res_cliente.grid(row=1, column=0, pady=(0, 8))

        ttk.Label(form, text="Servicio:").grid(row=2, column=0, sticky="w")
        self.combo_res_servicio = ttk.Combobox(form, textvariable=self.var_res_servicio,
                                               state="readonly", width=32)
        self.combo_res_servicio.grid(row=3, column=0, pady=(0, 8))
        self.combo_res_servicio.bind("<<ComboboxSelected>>", lambda _e: self._construir_parametros())

        ttk.Label(form, text="Fecha (AAAA-MM-DD):").grid(row=4, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_res_fecha, width=34).grid(row=5, column=0, pady=(0, 8))

        self.marco_parametros = ttk.LabelFrame(form, text="Parámetros del servicio", padding=8)
        self.marco_parametros.grid(row=6, column=0, sticky="ew", pady=4)
        self.vars_parametros = {}
        self._construir_parametros()

        botones = ttk.Frame(form)
        botones.grid(row=7, column=0, sticky="ew", pady=(8, 4))
        ttk.Button(botones, text="Cotizar", command=self._cotizar).pack(side="left", expand=True, fill="x")
        ttk.Button(botones, text="Confirmar reserva", command=self._crear_reserva).pack(
            side="left", expand=True, fill="x", padx=(6, 0))
        ttk.Label(form, textvariable=self.var_res_total, style="Total.TLabel").grid(
            row=8, column=0, sticky="w", pady=(6, 0))

        derecha = ttk.Frame(pagina)
        derecha.pack(side="left", fill="both", expand=True)
        marco, self.tabla_reservas = self._crear_tabla(derecha, [
            ("id", "ID", 70), ("cliente", "Cliente", 130), ("servicio", "Servicio", 140),
            ("fecha", "Fecha", 85), ("detalle", "Detalle", 190), ("total", "Total", 90),
            ("estado", "Estado", 85)])
        marco.pack(fill="both", expand=True)
        self.tabla_reservas.tag_configure("Confirmada", foreground="#1d6b2f")
        self.tabla_reservas.tag_configure("Cancelada", foreground="#777777")
        self.tabla_reservas.tag_configure("Fallida", foreground="#b00020")
        self.tabla_reservas.tag_configure("Error", foreground="#b00020")
        ttk.Button(derecha, text="Cancelar reserva seleccionada",
                   command=self._cancelar_reserva).pack(anchor="e", pady=(8, 0))

    def _servicio_seleccionado(self):
        id_servicio = id_de(self.var_res_servicio.get())
        return self.sistema.servicios.get(id_servicio)

    def _construir_parametros(self):
        """Muestra los campos que corresponden al tipo de servicio elegido (polimorfismo en la UI)."""
        for hijo in self.marco_parametros.winfo_children():
            hijo.destroy()
        self.vars_parametros = {}
        self.var_res_total.set("Total: —")
        servicio = self._servicio_seleccionado()
        if servicio is None:
            ttk.Label(self.marco_parametros, text="Seleccione un servicio.").pack(anchor="w")
            return

        def campo(clave, etiqueta, inicial):
            ttk.Label(self.marco_parametros, text=etiqueta).pack(anchor="w")
            var = tk.StringVar(value=inicial)
            ttk.Entry(self.marco_parametros, textvariable=var, width=30).pack(anchor="w", pady=(0, 4))
            self.vars_parametros[clave] = var

        def casilla(clave, etiqueta, inicial):
            var = tk.BooleanVar(value=inicial)
            ttk.Checkbutton(self.marco_parametros, text=etiqueta, variable=var).pack(anchor="w")
            self.vars_parametros[clave] = var

        if servicio.TIPO == "Sala":
            campo("horas", f"Horas (máx. {servicio.MAX_HORAS}):", "1")
            campo("asistentes", f"Asistentes (capacidad {servicio.capacidad}):", "1")
            campo("descuento", "Descuento (%):", "0")
            casilla("impuesto", "Aplicar IVA (19%)", True)
        elif servicio.TIPO == "Equipo":
            campo("dias", f"Días (máx. {servicio.MAX_DIAS}):", "1")
            casilla("seguro", f"Incluir seguro ({moneda(servicio.SEGURO_DIARIO)}/día)", False)
        else:
            campo("sesiones", f"Sesiones (máx. {servicio.MAX_SESIONES}):", "1")
            casilla("presencial", f"Presencial (+{moneda(servicio.RECARGO_PRESENCIAL)})", False)

    def _leer_parametros(self):
        """Convierte los campos del formulario en los argumentos de calcular_costo()."""
        v = self.vars_parametros
        servicio = self._servicio_seleccionado()
        if servicio is None:
            raise DatoInvalidoError("Debe seleccionar un servicio.")
        if servicio.TIPO == "Sala":
            return {"horas": a_decimal(v["horas"].get(), "Horas"),
                    "asistentes": a_entero(v["asistentes"].get(), "Asistentes"),
                    "descuento": a_decimal(v["descuento"].get() or "0", "Descuento"),
                    "impuesto": v["impuesto"].get()}
        if servicio.TIPO == "Equipo":
            return {"dias": a_entero(v["dias"].get(), "Días"), "seguro": v["seguro"].get()}
        return {"sesiones": a_entero(v["sesiones"].get(), "Sesiones"),
                "virtual": not v["presencial"].get()}

    def _cotizar(self):
        try:
            parametros = self._leer_parametros()
            total = self.sistema.cotizar(id_de(self.var_res_servicio.get()),
                                         self.var_res_fecha.get(), **parametros)
        except SoftwareFJError as e:
            self.var_res_total.set("Total: —")
            self._error(e, "No se puede cotizar")
        else:
            self.var_res_total.set(f"Total: {moneda(total)}")
            self.estado.set(f"Cotización: {moneda(total)} (servicio disponible en la fecha).")

    def _crear_reserva(self):
        try:
            id_cliente = id_de(self.var_res_cliente.get())
            if not id_cliente:
                raise DatoInvalidoError("Debe seleccionar un cliente.")
            parametros = self._leer_parametros()
            reserva = self.sistema.crear_reserva(id_cliente, id_de(self.var_res_servicio.get()),
                                                 self.var_res_fecha.get(), **parametros)
        except SoftwareFJError as e:
            self._error(e, "Reserva no realizada")
        else:
            self.var_res_total.set(f"Total: {moneda(reserva.costo_total)}")
            self._ok(f"Reserva {reserva.id_reserva} confirmada por {moneda(reserva.costo_total)}.")
        finally:
            # Siempre se actualizan las tablas (las reservas fallidas quedan en el historial)
            self._refrescar_reservas()
            self._refrescar_servicios()
            self._refrescar_clientes()

    def _cancelar_reserva(self):
        seleccion = self.tabla_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una reserva de la tabla.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", f"¿Cancelar la reserva {seleccion[0]}?", parent=self):
            return
        try:
            self.sistema.cancelar_reserva(seleccion[0])
        except SoftwareFJError as e:
            self._error(e, "Operación no permitida")
        else:
            self._ok(f"Reserva {seleccion[0]} cancelada. La fecha quedó libre nuevamente.")
        finally:
            self._refrescar_reservas()
            self._refrescar_servicios()
            self._refrescar_clientes()

    def _refrescar_reservas(self):
        self.tabla_reservas.delete(*self.tabla_reservas.get_children())
        for r in reversed(list(self.sistema.reservas.values())):
            self.tabla_reservas.insert(
                "", "end", iid=r.id_reserva, tags=(r.estado,),
                values=(r.id_reserva, r.cliente.nombre, r.servicio.nombre,
                        r.fecha.isoformat() if r.fecha else "—",
                        self.sistema.describir_parametros(r),
                        moneda(r.costo_total) if r.estado in ("Confirmada", "Cancelada") else "—",
                        r.estado))

    def _refrescar_combos_reserva(self):
        clientes = [f"{c.id_entidad} | {c.nombre}" for c in self.sistema.clientes.values()]
        servicios = [f"{s.id_entidad} | {s.TIPO}: {s.nombre}" + ("" if s.disponible else " (fuera de servicio)")
                     for s in self.sistema.servicios.values()]
        self.combo_res_cliente["values"] = clientes
        self.combo_res_servicio["values"] = servicios
        if self.var_res_cliente.get() not in clientes:
            self.var_res_cliente.set("")
        if self.var_res_servicio.get() not in servicios:
            # Conserva la selección si solo cambió su estado de disponibilidad
            actual = id_de(self.var_res_servicio.get())
            coincidencia = next((s for s in servicios if id_de(s) == actual), "")
            self.var_res_servicio.set(coincidencia)
            if not coincidencia:
                self._construir_parametros()

    # ------------------------------------------------------ pruebas / log
    def _pestana_pruebas(self):
        pagina = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(pagina, text="  Log  ")

        botones = ttk.Frame(pagina)
        botones.pack(fill="x")
        ttk.Button(botones, text="Ver sistema.log", command=self._ver_log).pack(side="left", padx=(0, 6))
        ttk.Button(botones, text="Limpiar", command=lambda: self.salida.delete("1.0", "end")).pack(side="left")

        marco = ttk.Frame(pagina)
        marco.pack(fill="both", expand=True, pady=(8, 0))
        self.salida = tk.Text(marco, wrap="word", font=("Consolas", 10))
        scroll = ttk.Scrollbar(marco, command=self.salida.yview)
        self.salida.configure(yscrollcommand=scroll.set)
        self.salida.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _ver_log(self):
        self.salida.delete("1.0", "end")
        try:
            with open(RUTA_LOG, encoding="utf-8", errors="replace") as archivo:
                lineas = archivo.readlines()[-300:]
        except FileNotFoundError:
            self.salida.insert("end", "Aún no existe el archivo sistema.log.")
        else:
            self.salida.insert("end", "".join(lineas) or "El log está vacío.")
            self.salida.see("end")


def iniciar_interfaz():
    app = AplicacionSoftwareFJ()
    app.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
