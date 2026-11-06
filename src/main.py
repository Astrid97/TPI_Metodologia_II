import os
from datetime import datetime

from sistema_solicitudes import GestorSolicitudesAcademicas
from sistema_solicitudes import DatosSolicitud


def ejecutar_escenario_demostracion():
    """
    Ejecuta un lote completo de pruebas funcionales verificables.
    Permite comparar el comportamiento externo ANTES y DESPUÉS del refactoring.
    """
    archivo_demo = "solicitudes_db.json"
    if os.path.exists(archivo_demo):
        os.remove(archivo_demo)

    gestor = GestorSolicitudesAcademicas(archivo_demo)

    print("=======================================================")
    print("  INICIANDO DEMOSTRACIÓN DEL SISTEMA BASE (ESTADO INICIAL)")
    print("=======================================================")

    # 1. Registro de solicitudes válidas
    gestor.procesar_solicitud(
        DatosSolicitud(
            id_solicitud=101,
            nombre="Juan",
            apellido="Pérez",
            legajo=114520,
            dni="42111222",
            email="juan.perez@tupad.utn.edu.ar",
            condicion="REG",
            materias_aprobadas=12,
            tipo_solicitud="EQUIV",
            prioridad="ALTA",
            descripcion="Solicitud de equivalencia de Análisis Matemático I",
            fecha="2026-04-10",
        )
    )
    gestor.procesar_solicitud(
        DatosSolicitud(
            id_solicitud=102,
            nombre="María",
            apellido="López",
            legajo=118930,
            dni="43555666",
            email="maria.lopez@tupad.utn.edu.ar",
            condicion="REG",
            materias_aprobadas=8,
            tipo_solicitud="CERT",
            prioridad="MEDIA",
            descripcion="Certificado de alumno regular para presentar en el trabajo",
            fecha="2026-04-10",
        )
    )
    gestor.procesar_solicitud(
        DatosSolicitud(
            id_solicitud=103,
            nombre="Lucas",
            apellido="Martínez",
            legajo=120045,
            dni="44888999",
            email="lucas.martinez@tupad.utn.edu.ar",
            condicion="LIBRE",
            materias_aprobadas=4,
            tipo_solicitud="EXCEP",
            prioridad="ALTA",
            descripcion="Excepción de correlatividad para cursar Metodología II",
            fecha="2026-04-11",
        )
    )

    # 2. Caso de validación rechazada (Estudiante libre con menos de 2 materias)
    gestor.procesar_solicitud(
        DatosSolicitud(
            id_solicitud=104,
            nombre="Pedro",
            apellido="Gómez",
            legajo=125001,
            dni="45000111",
            email="pedro.gomez@tupad.utn.edu.ar",
            condicion="LIBRE",
            materias_aprobadas=1,
            tipo_solicitud="CERT",
            prioridad="BAJA",
            descripcion="Certificado de materias rendidas",
            fecha="2026-04-11",
        )
    )

    # 3. Cambio de estados
    print("\n--- Ejecutando cambios de estado ---")
    gestor.cambiar_estado(
        101, "REV", "Documentación recibida en Secretaría Académica", "2026-04-12"
    )
    gestor.cambiar_estado(
        102, "APR", "Certificado emitido y enviado por correo", "2026-04-12"
    )

    # 4. Reasignación de responsable
    print("\n--- Ejecutando reasignación de responsable ---")
    gestor.asignar_responsable(
        103, "Dirección de Carrera TUP", "Mg. Sofía Peralta", "tup@utn.edu.ar"
    )

    # 5. Búsqueda filtrada
    gestor.buscar_solicitudes(legajo=114520)

    # 6. Reporte general
    gestor.generar_reporte()


def menu_principal():
    gestor = GestorSolicitudesAcademicas()
    while True:
        print("\n--- SISTEMA DE GESTIÓN DE SOLICITUDES ACADÉMICAS ---")
        print("1. Registrar nueva solicitud")
        print("2. Cambiar estado de solicitud")
        print("3. Asignar/Reasignar responsable")
        print("4. Buscar solicitudes por legajo")
        print("5. Generar reporte general")
        print("6. Ejecutar escenario de demostración completo (Datos de prueba)")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                id_sol = int(input("ID Solicitud (ej. 105): "))
                nombre = input("Nombre del estudiante: ")
                apellido = input("Apellido del estudiante: ")
                legajo = int(input("Legajo (5-6 dígitos): "))
                dni = input("DNI: ")
                email = input("Email: ")
                condicion = input("Condición (REG/LIBRE/EGR): ").upper()
                materias = int(input("Cantidad de materias aprobadas: "))
                tipo = input("Tipo trámite (EQUIV/CERT/EXCEP/BAJA): ").upper()
                prioridad = input("Prioridad (ALTA/MEDIA/BAJA): ").upper()
                desc = input("Descripción del pedido: ")
                fecha = datetime.now().strftime("%Y-%m-%d")
                gestor.procesar_solicitud(
                    DatosSolicitud(
                        id_solicitud=id_sol,
                        nombre=nombre,
                        apellido=apellido,
                        legajo=legajo,
                        dni=dni,
                        email=email,
                        condicion=condicion,
                        materias_aprobadas=materias,
                        tipo_solicitud=tipo,
                        prioridad=prioridad,
                        descripcion=desc,
                        fecha=fecha,
                    )
                )
            except ValueError:
                print(
                    "[ERROR] Ingrese valores numéricos válidos para ID, legajo y materias."
                )
        elif opcion == "2":
            try:
                id_sol = int(input("ID de la solicitud: "))
                nuevo_est = input("Nuevo estado (PEND/REV/APR/RECH): ").upper()
                obs = input("Observación: ")
                fecha = datetime.now().strftime("%Y-%m-%d")
                gestor.cambiar_estado(id_sol, nuevo_est, obs, fecha)
            except ValueError:
                print("[ERROR] ID inválido.")
        elif opcion == "3":
            try:
                id_sol = int(input("ID de la solicitud: "))
                area = input("Nombre de la nueva área: ")
                resp = input("Nombre del responsable a cargo: ")
                mail = input("Email del área: ")
                gestor.asignar_responsable(id_sol, area, resp, mail)
            except ValueError:
                print("[ERROR] ID inválido.")
        elif opcion == "4":
            try:
                leg = int(input("Ingrese el legajo a buscar: "))
                gestor.buscar_solicitudes(legajo=leg)
            except ValueError:
                print("[ERROR] Legajo inválido.")
        elif opcion == "5":
            gestor.generar_reporte()
        elif opcion == "6":
            ejecutar_escenario_demostracion()
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu_principal()
