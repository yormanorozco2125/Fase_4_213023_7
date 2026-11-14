# Fase_4_213023_7
Tarea colaborativa de la fase 4 — Sistema de gestión Software FJ.

## Ejecución
```bash
python main.py            # Abre la interfaz gráfica (Tkinter)
python main.py --pruebas  # Ejecuta por consola las 11 operaciones de prueba
```

## Módulos
| Archivo | Contenido |
|---|---|
| `excepciones_y_clases_bases.py` | Jerarquía de excepciones, clase abstracta `Entidad`, configuración de logging |
| `clientes_servicios.py` | `Cliente`, `Servicio` (abstracta) y servicios `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`, validaciones y control de disponibilidad por fecha |
| `gestion_reservas.py` | Clase `Reserva` (try/except/else/finally), validación de fechas y las 11 pruebas |
| `sistema_gestion.py` | `SistemaGestion`: administra clientes, servicios y reservas de forma dinámica |
| `interfaz_grafica.py` | Interfaz Tkinter con pestañas Clientes, Servicios, Reservas y Log |

## Funcionalidades de la interfaz
- **Clientes:** registrar (nombre solo letras, correo válido y no repetido), listar y eliminar (solo si no tiene reservas activas).
- **Servicios:** registrar salas, equipos y asesorías; activar o desactivar (fuera de servicio); ver las fechas ocupadas.
- **Reservas:** elegir cliente, servicio y fecha; los parámetros cambian según el tipo de servicio; cotizar, confirmar y cancelar.
- **Control de disponibilidad:** un servicio no se puede reservar dos veces en la misma fecha ni si está fuera de servicio; las salas validan la capacidad; al cancelar, la fecha queda libre.
- **Log:** consultar `sistema.log` desde la interfaz.

Menú *Archivo → Cargar datos de ejemplo* carga registros de prueba.
