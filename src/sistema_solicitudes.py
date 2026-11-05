import json
import os
from datetime import datetime, timedelta
from enum import StrEnum        

class CodigoEstado(StrEnum):
    PENDIENTE = "PEND"
    EN_REVISION = "REV"
    APROBADA = "APR"
    RECHAZADA = "RECH"
    
class TipoSolicitud(StrEnum):
    EQUIVALENCIA = "EQUIV"
    CERTIFICADO = "CERT"
    EXCEPCION_CORRELATIVIDAD = "EXCEP"
    BAJA = "BAJA"
    
class Prioridad(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
    
class CondicionEstudiante(StrEnum):
    REGULAR = "REG"
    LIBRE = "LIBRE"
    EGRESADO = "EGR"
    
class Estado:
    """Representa el estado actual de una solicitud académica."""

    def __init__(self, codigo: CodigoEstado, descripcion, fecha_actualizacion):
        self.codigo = codigo
        self.descripcion = descripcion
        self.fecha_actualizacion = fecha_actualizacion
        
class Estudiante:
    """Representa al estudiante que realiza la solicitud."""
    
    #---- Constantes
    LEGAJO_MINIMO = 10000
    LEGAJO_MAXIMO = 999999
    MATERIAS_MINIMAS_LIBRE = 2

    def __init__(
        self, nombre, apellido, legajo, dni, email, condicion, materias_aprobadas
    ):
        self.nombre = nombre
        self.apellido = apellido
        self.legajo = legajo
        self.dni = dni
        self.email = email
        self.condicion = condicion
        self.materias_aprobadas = materias_aprobadas
        
    def validar_legajo_y_regularidad_estudiante(self):
        if self.legajo < self.LEGAJO_MINIMO or self.legajo > self.LEGAJO_MAXIMO:
            return False, f"El legajo debe tener entre 5 y 6 dígitos ({self.LEGAJO_MINIMO} - {self.LEGAJO_MAXIMO})."
        if "@" not in self.email or "." not in self.email:
            return False, "El email del estudiante no tiene un formato válido."
        if (
            self.condicion == CondicionEstudiante.LIBRE
            and self.materias_aprobadas < self.MATERIAS_MINIMAS_LIBRE
        ):
            return (
                False,
                f"Estudiante libre con menos de {self.MATERIAS_MINIMAS_LIBRE} materias aprobadas no puede iniciar trámites.",
            )
        return True, "Estudiante válido."

class ResponsableArea:
    """Representa el área administrativa o académica asignada."""

    def __init__(self, nombre_area, responsable_cargo, email_contacto):
        self.nombre_area = nombre_area
        self.responsable_cargo = responsable_cargo
        self.email_contacto = email_contacto


class Solicitud:
    """Representa una solicitud académica realizada por un estudiante."""

    def __init__(
        self,
        id_solicitud,
        estudiante,
        tipo,
        prioridad,
        descripcion,
        fecha_creacion,
        estado,
        area_responsable,
        dias_vencimiento,
    ):
        self.id_solicitud = id_solicitud
        self.estudiante = estudiante
        self.tipo = tipo
        self.prioridad = prioridad
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion
        self.estado = estado
        self.area_responsable = area_responsable
        self.dias_vencimiento = dias_vencimiento


class GestorSolicitudesAcademicas:
    """Clase encargada de gestionar las operaciones sobre las solicitudes."""

    def __init__(self, archivo_db="solicitudes_db.json"):
        self.archivo_db = archivo_db
        
    def _leer_datos(self):
        with open(self.archivo_db, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def _guardar_datos(self, datos):
        with open(self.archivo_db, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def procesar_solicitud(
        self,
        id_solicitud,
        nombre_est,
        apellido_est,
        legajo_est,
        dni_est,
        email_est,
        condicion_est,
        materias_aprobadas,
        tipo_solicitud,
        prioridad,
        descripcion,
        fecha_str,
    ):
        print(f"\n[PROCESANDO] Iniciando registro de solicitud #{id_solicitud}...")

        # Validación de datos de entrada
        if not nombre_est or not apellido_est or not dni_est or not descripcion:
            print("[ERROR] Nombre, apellido, DNI y descripción son obligatorios.")
            return False

        if tipo_solicitud not in list(TipoSolicitud):
            print(f"[ERROR] Tipo de solicitud '{tipo_solicitud}' no reconocido.")
            return False

        if prioridad not in list(Prioridad):
            print(f"[ERROR] Prioridad '{prioridad}' inválida.")
            return False

        # Instanciación inicial de objetos
        est = Estudiante(
            nombre_est,
            apellido_est,
            legajo_est,
            dni_est,
            email_est,
            condicion_est,
            materias_aprobadas,
        )
        est_inicial = Estado(CodigoEstado.PENDIENTE, "Pendiente de revisión inicial", fecha_str)
        resp_prov = ResponsableArea("Sin asignar", "Sin asignar", "")
        sol = Solicitud(
            id_solicitud,
            est,
            tipo_solicitud,
            prioridad,
            descripcion,
            fecha_str,
            est_inicial,
            resp_prov,
            0,
        )

        # Verificación de condiciones académicas del estudiante
        es_valido, mensaje_val = est.validar_legajo_y_regularidad_estudiante()
        if not es_valido:
            print(f"[RECHAZADA EN VALIDACIÓN] {mensaje_val}")
            return False

        # Asignación de área responsable y cálculo de días de gestión según trámite
        if tipo_solicitud == TipoSolicitud.EQUIVALENCIA:
            if est.condicion != CondicionEstudiante.REGULAR:
                print(
                    "[ERROR] Las equivalencias solo pueden ser solicitadas por alumnos REGULARES."
                )
                return False
            area = ResponsableArea(
                "Secretaría Académica", "Dra. Laura Fernandez", "academica@utn.edu.ar"
            )
            if prioridad == Prioridad.ALTA:
                dias = 7
            elif prioridad == Prioridad.MEDIA:
                dias = 15
            else:
                dias = 30
        elif tipo_solicitud == TipoSolicitud.CERTIFICADO:
            area = ResponsableArea(
                "Departamento de Alumnado", "Lic. Fernando Ruiz", "alumnado@utn.edu.ar"
            )
            if prioridad == Prioridad.ALTA:
                dias = 2
            elif prioridad == Prioridad.MEDIA:
                dias = 5
            else:
                dias = 10
        elif tipo_solicitud == TipoSolicitud.EXCEPCION_CORRELATIVIDAD:
            area = ResponsableArea(
                "Consejo Directivo", "Ing. Roberto Díaz", "consejo@utn.edu.ar"
            )
            if prioridad == Prioridad.ALTA:
                dias = 5
            else:
                dias = 20
        else:  # Caso "BAJA"
            area = ResponsableArea(
                "Departamento de Alumnado", "Lic. Fernando Ruiz", "alumnado@utn.edu.ar"
            )
            dias = 3

        sol.area_responsable = area
        sol.dias_vencimiento = dias

        # Cálculo de fecha de vencimiento
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
        fecha_venc = (fecha_obj + timedelta(days=dias)).strftime("%Y-%m-%d")

        # Lectura y guardado en archivo JSON
        datos = []
        if os.path.exists(self.archivo_db):
            try:
                datos = self._leer_datos()
            except Exception:
                datos = []

        for item in datos:
            if item["id_solicitud"] == id_solicitud:
                print(f"[ERROR] Ya existe una solicitud con el ID {id_solicitud}.")
                return False

        nuevo_registro = {
            "id_solicitud": sol.id_solicitud,
            "estudiante": {
                "nombre": est.nombre,
                "apellido": est.apellido,
                "legajo": est.legajo,
                "dni": est.dni,
                "email": est.email,
                "condicion": est.condicion,
                "materias_aprobadas": est.materias_aprobadas,
            },
            "tipo": sol.tipo,
            "prioridad": sol.prioridad,
            "descripcion": sol.descripcion,
            "fecha_creacion": sol.fecha_creacion,
            "fecha_vencimiento": fecha_venc,
            "dias_vencimiento": sol.dias_vencimiento,
            "estado": {
                "codigo": sol.estado.codigo,
                "descripcion": sol.estado.descripcion,
                "fecha_actualizacion": sol.estado.fecha_actualizacion,
            },
            "area_responsable": {
                "nombre_area": sol.area_responsable.nombre_area,
                "responsable_cargo": sol.area_responsable.responsable_cargo,
                "email_contacto": sol.area_responsable.email_contacto,
            },
        }

        datos.append(nuevo_registro)
        self._guardar_datos(datos)

        print(
            f"[OK] Solicitud #{id_solicitud} registrada con éxito. Área: {area.nombre_area} (Plazo: {dias} días, vence: {fecha_venc})."
        )
        return True

    def cambiar_estado(
        self, id_solicitud, nuevo_codigo_estado, observacion, fecha_actualizacion
    ):
        if not os.path.exists(self.archivo_db):
            print("[ERROR] No hay solicitudes registradas.")
            return False

        datos = self._leer_datos()

        if nuevo_codigo_estado not in list(CodigoEstado):
            print(f"[ERROR] Código de estado '{nuevo_codigo_estado}' inválido.")
            return False

        encontrado = False
        for item in datos:
            if item["id_solicitud"] == id_solicitud:
                if (
                    item["estado"]["codigo"] in [CodigoEstado.APROBADA, CodigoEstado.RECHAZADA]
                    and nuevo_codigo_estado == CodigoEstado.PENDIENTE
                ):
                    print(
                        "[ERROR] No se puede reabrir a PENDIENTE una solicitud ya finalizada."
                    )
                    return False

                item["estado"]["codigo"] = nuevo_codigo_estado
                item["estado"]["descripcion"] = observacion
                item["estado"]["fecha_actualizacion"] = fecha_actualizacion
                encontrado = True
                break

        if not encontrado:
            print(f"[ERROR] No se encontró la solicitud #{id_solicitud}.")
            return False

        self._guardar_datos(datos)
        
        print(
            f"[OK] Estado de solicitud #{id_solicitud} actualizado a '{nuevo_codigo_estado}' ({observacion})."
        )
        return True

    def asignar_responsable(
        self, id_solicitud, nueva_area, nuevo_responsable, nuevo_email
    ):
        if not os.path.exists(self.archivo_db):
            print("[ERROR] No hay solicitudes registradas.")
            return False

        datos = self._leer_datos()

        encontrado = False
        for item in datos:
            if item["id_solicitud"] == id_solicitud:
                item["area_responsable"]["nombre_area"] = nueva_area
                item["area_responsable"]["responsable_cargo"] = nuevo_responsable
                item["area_responsable"]["email_contacto"] = nuevo_email
                encontrado = True
                break

        if not encontrado:
            print(f"[ERROR] No se encontró la solicitud #{id_solicitud}.")
            return False

        self._guardar_datos(datos)

        print(
            f"[OK] Solicitud #{id_solicitud} reasignada a {nueva_area} ({nuevo_responsable})."
        )
        return True

    def buscar_solicitudes(self, legajo=None, codigo_estado=None):
        if not os.path.exists(self.archivo_db):
            print("[INFO] Base de datos vacía.")
            return []

        datos = self._leer_datos()

        resultado = []
        for s in datos:
            cumple_legajo = (legajo is None) or (s["estudiante"]["legajo"] == legajo)
            cumple_estado = (codigo_estado is None) or (
                s["estado"]["codigo"] == codigo_estado
            )
            if cumple_legajo and cumple_estado:
                resultado.append(s)

        print(f"\n--- RESULTADOS DE BÚSQUEDA (Encontradas: {len(resultado)}) ---")
        for r in resultado:
            print(
                f"ID #{r['id_solicitud']} | Legajo: {r['estudiante']['legajo']} ({r['estudiante']['apellido']}, {r['estudiante']['nombre']}) "
                f"| Tipo: {r['tipo']} | Prioridad: {r['prioridad']} | Estado: {r['estado']['codigo']} "
                f"| Área: {r['area_responsable']['nombre_area']}"
            )
        return resultado

    def generar_reporte(self):
        if not os.path.exists(self.archivo_db):
            print("[INFO] No hay datos para generar el reporte.")
            return

        solicitudes = self._leer_datos()

        pendiente = 0
        en_revision = 0
        aprobada = 0
        rechazada = 0
        prioridad_alta = 0

        for solicitud in solicitudes:
            if solicitud["estado"]["codigo"] == CodigoEstado.PENDIENTE:
                pendiente += 1
            elif solicitud["estado"]["codigo"] == CodigoEstado.EN_REVISION:
                en_revision += 1
            elif solicitud["estado"]["codigo"] == CodigoEstado.APROBADA:
                aprobada += 1
            elif solicitud["estado"]["codigo"] == CodigoEstado.RECHAZADA:
                rechazada += 1

            if solicitud["prioridad"] == Prioridad.ALTA:
                prioridad_alta += 1

        print("\n=======================================================")
        print("       REPORTE GENERAL DE SOLICITUDES ACADÉMICAS       ")
        print("=======================================================")
        print(f"Total de solicitudes registradas : {len(solicitudes)}")
        print(f"  - Pendientes (PEND)            : {pendiente}")
        print(f"  - En Revisión (REV)            : {en_revision}")
        print(f"  - Aprobadas (APR)              : {aprobada}")
        print(f"  - Rechazadas (RECH)            : {rechazada}")
        print(f"Solicitudes de prioridad ALTA    : {prioridad_alta}")
        print("-------------------------------------------------------")
        print("Detalle de solicitudes:")
        for solicitud in solicitudes:
            print(
                f"  [#{solicitud['id_solicitud']}] {solicitud['fecha_creacion']} (Vence: {solicitud['fecha_vencimiento']}) - "
                f"{solicitud['estudiante']['apellido']}, {solicitud['estudiante']['nombre']} (Leg: {solicitud['estudiante']['legajo']}) - "
                f"Trámite: {solicitud['tipo']} [{solicitud['estado']['codigo']}] -> {solicitud['area_responsable']['responsable_cargo']}"
            )
        print("=======================================================\n")