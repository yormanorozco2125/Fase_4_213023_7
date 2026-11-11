# Importamos la función de pruebas unificada las partes de gestión de reservas
from gestion_reservas import correr_pruebas

def main():
    print("==================================================")
    print("      SISTEMA DE GESTIÓN - SOFTWARE FJ (FASE 4)   ")
    print("==================================================\n")
    
    # Ejecutamos las 11 pruebas integradas del grupo
    correr_pruebas()

if __name__ == "__main__":
    main()