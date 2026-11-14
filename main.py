"""Punto de entrada del sistema Software FJ (Fase 4).

Uso:
    python main.py            -> Abre la interfaz gráfica (Tkinter) para gestionar
                                 clientes, servicios y reservas de forma dinámica.
    python main.py --pruebas  -> Ejecuta por consola las 11 operaciones de prueba.
"""
import sys

from gestion_reservas import correr_pruebas


def main():
    if "--pruebas" in sys.argv:
        print("==================================================")
        print("      SISTEMA DE GESTIÓN - SOFTWARE FJ (FASE 4)   ")
        print("==================================================\n")
        correr_pruebas()
        return

    from interfaz_grafica import iniciar_interfaz
    iniciar_interfaz()


if __name__ == "__main__":
    main()
