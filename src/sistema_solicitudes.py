import json
import os
from datetime import datetime, timedelta
from enum import StrEnum
from dataclasses import dataclass


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


# ---------- Reglas de seleccion de plazos y areas por tipo de solicitud ----------

PLAZOS_DIAS = {
    TipoSolicitud.EQUIVALENCIA: {
        Prioridad.ALTA: 7,
        Prioridad.MEDIA: 15,
        Prioridad.BAJA: 30,
    },
    TipoSolicitud.CERTIFICADO: {
        Prioridad.ALTA: 2,
        Prioridad.MEDIA: 5,
        Prioridad.BAJA: 10,
    },
    TipoSolicitud.EXCEPCION_CORRELATIVIDAD: {
        Prioridad.ALTA: 5,
        Prioridad.MEDIA: 20,
        Prioridad.BAJA: 20,
    },
    TipoSolicitud.BAJA: {Prioridad.ALTA: 3, Prioridad.MEDIA: 3, Prioridad.BAJA: 3},
}

AREAS_POR_TIPO = {
    TipoSolicitud.EQUIVALENCIA: (
        "Secretaría Académica",
        "Dra. Laura Fernandez",
        "academica@utn.edu.ar",
    ),
    TipoSolicitud.CERTIFICADO: (
        "Departamento de Alumnado",
        "Lic. Fernando Ruiz",
        "alumnado@utn.edu.ar",
    ),
    TipoSolicitud.EXCEPCION_CORRELATIVIDAD: (
        "Consejo Directivo",
        "Ing. Roberto Díaz",
        "consejo@utn.edu.ar",
    ),
    TipoSolicitud.BAJA: (
        "Departamento de Alumnado",
        "Lic. Fernando Ruiz",
        "alumnado@utn.edu.ar",
    ),
}


class Estado:
    """Representa el estado actual de una solicitud académica."""

    def __init__(self, codigo: CodigoEstado, descripcion, fecha_actualizacion):
        self.codigo = codigo
        self.descripcion = descripcion
        self.fecha_actualizacion = fecha_actualizacion

    def convertir_a_diccionario(self):
        return {
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "fecha_actualizacion": self.fecha_actualizacion,
        }


class Estudiante:
    """Representa al estudiante que realiza la solicitud."""

    # ---- Constantes
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

    def convertir_a_diccionario(self):
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "legajo": self.legajo,
            "dni": self.dni,
            "email": self.email,
            "condicion": self.condicion,
            "materias_aprobadas": self.materias_aprobadas,
        }

    def validar_legajo_y_regularidad_estudiante(self):
        if self.legajo < self.LEGAJO_MINIMO or self.legajo > self.LEGAJO_MAXIMO:
            return (
                False,
                f"El legajo debe tener entre 5 y 6 dígitos ({self.LEGAJO_MINIMO} - {self.LEGAJO_MAXIMO}).",
            )
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

    def convertir_a_diccionario(self):
        return {
            "nombre_area": self.nombre_area,
            "responsable_cargo": self.responsable_cargo,
            "email_contacto": self.email_contacto,
        }


class Solicitud:
    """Representa una solicitud académica realizada por un estudiante."""

    FORMATO_FECHA = "%Y-%m-%d"

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

    def calcular_fecha_vencimiento(self):
        fecha_creacion = datetime.strptime(self.fecha_creacion, self.FORMATO_FECHA)
        fecha_vencimiento = fecha_creacion + timedelta(days=self.dias_vencimiento)
        return fecha_vencimiento.strftime(self.FORMATO_FECHA)

    def convertir_a_diccionario(self):
        return {
            "id_solicitud": self.id_solicitud,
            "estudiante": self.estudiante.convertir_a_diccionario(),
            "tipo": self.tipo,
            "prioridad": self.prioridad,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion,
            "fecha_vencimiento": self.calcular_fecha_vencimiento(),
            "dias_vencimiento": self.dias_vencimiento,
            "estado": self.estado.convertir_a_diccionario(),
            "area_responsable": self.area_responsable.convertir_a_diccionario(),
        }


class RepositorioSolicitudes:
    """Responsable de leer y guardar las solicitudes en el archivo JSON."""

    def __init__(self, archivo_db):
        self.archivo_db = archivo_db

    def existe(self):
        return os.path.exists(self.archivo_db)

    def leer(self):
        with open(self.archivo_db, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def guardar(self, datos):
        with open(self.archivo_db, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def _obtener_solicitudes(self):
        if not self.existe():
            return []
        try:
            return self.leer()
        except Exception:
            return []

    def existe_id_solicitud(self, id_solicitud):
        for solicitud in self._obtener_solicitudes():
            if solicitud["id_solicitud"] == id_solicitud:
                return True
        return False

    def agregar_solicitud(self, datos_solicitud):
        solicitudes = self._obtener_solicitudes()
        solicitudes.append(datos_solicitud)
        self.guardar(solicitudes)


@dataclass(frozen=True)
class DatosSolicitud:
    """Corresponde a los datos que se ingresan para registrar una nueva solocitud"""

    id_solicitud: int
    nombre: str
    apellido: str
    legajo: int
    dni: str
    email: str
    condicion: str
    materias_aprobadas: int
    tipo_solicitud: str
    prioridad: str
    descripcion: str
    fecha: str


class GestorSolicitudesAcademicas:
    """Clase encargada de gestionar las operaciones sobre las solicitudes."""

    def __init__(
        self, archivo_db="solicitudes_db.json", repositorio=None, mostrar=print
    ):
        self.repositorio = repositorio or RepositorioSolicitudes(archivo_db)
        self.mostrar = mostrar

    def _validar_datos_entrada(self, datos: DatosSolicitud):
        if (
            not datos.nombre
            or not datos.apellido
            or not datos.dni
            or not datos.descripcion
        ):
            self.mostrar(
                "[ERROR] Nombre, apellido, DNI y descripción son obligatorios."
            )
            return False

        if datos.tipo_solicitud not in list(TipoSolicitud):
            self.mostrar(
                f"[ERROR] Tipo de solicitud '{datos.tipo_solicitud}' no reconocido."
            )
            return False

        if datos.prioridad not in list(Prioridad):
            self.mostrar(f"[ERROR] Prioridad '{datos.prioridad}' inválida.")
            return False
        return True

    def _verificar_condiciones_academicas(self, est, tipo_solicitud):
        es_valido, mensaje_val = est.validar_legajo_y_regularidad_estudiante()
        if not es_valido:
            self.mostrar(f"[RECHAZADA EN VALIDACIÓN] {mensaje_val}")
            return False

        # Regla especial que no está en las tablas porque depende del estudiante
        # y del tipo de trámite: las equivalencias solo pueden pedirlas alumnos regulares
        if (
            tipo_solicitud == TipoSolicitud.EQUIVALENCIA
            and est.condicion != CondicionEstudiante.REGULAR
        ):
            self.mostrar(
                "[ERROR] Las equivalencias solo pueden ser solicitadas por alumnos REGULARES."
            )
            return False
        return True

    def procesar_solicitud(self, datos: DatosSolicitud):
        self.mostrar(
            f"\n[PROCESANDO] Iniciando registro de solicitud #{datos.id_solicitud}..."
        )

        if not self._validar_datos_entrada(datos):
            return False

        # Convertir los textos recibidos a enum (necesario para buscar en
        # PLAZOS_DIAS y AREAS_POR_TIPO)

        tipo_solicitud = TipoSolicitud(datos.tipo_solicitud)
        prioridad = Prioridad(datos.prioridad)

        # Instanciación inicial de objetos
        est = Estudiante(
            datos.nombre,
            datos.apellido,
            datos.legajo,
            datos.dni,
            datos.email,
            datos.condicion,
            datos.materias_aprobadas,
        )

        est_inicial = Estado(
            CodigoEstado.PENDIENTE, "Pendiente de revisión inicial", datos.fecha
        )

        resp_prov = ResponsableArea("Sin asignar", "Sin asignar", "")

        sol = Solicitud(
            datos.id_solicitud,
            est,
            tipo_solicitud,
            prioridad,
            datos.descripcion,
            datos.fecha,
            est_inicial,
            resp_prov,
            0,
        )
        if not self._verificar_condiciones_academicas(est, tipo_solicitud):
            return False

        # Asignación de área responsable y plazo según tipo y prioridad
        # (*) desagrupa los elementos de la tupla y los pasa uno a uno
        area = ResponsableArea(*AREAS_POR_TIPO[tipo_solicitud])
        dias = PLAZOS_DIAS[tipo_solicitud][prioridad]

        sol.area_responsable = area
        sol.dias_vencimiento = dias

        fecha_venc = sol.calcular_fecha_vencimiento()

        if self.repositorio.existe_id_solicitud(datos.id_solicitud):
            self.mostrar(
                f"[ERROR] Ya existe una solicitud con el ID {datos.id_solicitud}."
            )
            return False

        # Agregar solicitud con formato diccionario al repositorio
        self.repositorio.agregar_solicitud(sol.convertir_a_diccionario())

        self.mostrar(
            f"[OK] Solicitud #{datos.id_solicitud} registrada con éxito. Área: {area.nombre_area} (Plazo: {dias} días, vence: {fecha_venc})."
        )
        return True

    def cambiar_estado(
        self, id_solicitud, nuevo_codigo_estado, observacion, fecha_actualizacion
    ):
        if not self.repositorio.existe():
            self.mostrar("[ERROR] No hay solicitudes registradas.")
            return False

        datos = self.repositorio.leer()

        if nuevo_codigo_estado not in list(CodigoEstado):
            self.mostrar(f"[ERROR] Código de estado '{nuevo_codigo_estado}' inválido.")
            return False

        encontrado = False
        for item in datos:
            if item["id_solicitud"] == id_solicitud:
                if (
                    item["estado"]["codigo"]
                    in [CodigoEstado.APROBADA, CodigoEstado.RECHAZADA]
                    and nuevo_codigo_estado == CodigoEstado.PENDIENTE
                ):
                    self.mostrar(
                        "[ERROR] No se puede reabrir a PENDIENTE una solicitud ya finalizada."
                    )
                    return False

                item["estado"]["codigo"] = nuevo_codigo_estado
                item["estado"]["descripcion"] = observacion
                item["estado"]["fecha_actualizacion"] = fecha_actualizacion
                encontrado = True
                break

        if not encontrado:
            self.mostrar(f"[ERROR] No se encontró la solicitud #{id_solicitud}.")
            return False

        self.repositorio.guardar(datos)

        self.mostrar(
            f"[OK] Estado de solicitud #{id_solicitud} actualizado a '{nuevo_codigo_estado}' ({observacion})."
        )
        return True

    def asignar_responsable(
        self, id_solicitud, nueva_area, nuevo_responsable, nuevo_email
    ):
        if not self.repositorio.existe():
            self.mostrar("[ERROR] No hay solicitudes registradas.")
            return False

        datos = self.repositorio.leer()

        encontrado = False
        for item in datos:
            if item["id_solicitud"] == id_solicitud:
                item["area_responsable"]["nombre_area"] = nueva_area
                item["area_responsable"]["responsable_cargo"] = nuevo_responsable
                item["area_responsable"]["email_contacto"] = nuevo_email
                encontrado = True
                break

        if not encontrado:
            self.mostrar(f"[ERROR] No se encontró la solicitud #{id_solicitud}.")
            return False

        self.repositorio.guardar(datos)

        self.mostrar(
            f"[OK] Solicitud #{id_solicitud} reasignada a {nueva_area} ({nuevo_responsable})."
        )
        return True

    def buscar_solicitudes(self, legajo=None, codigo_estado=None):
        if not self.repositorio.existe():
            self.mostrar("[INFO] Base de datos vacía.")
            return []

        datos = self.repositorio.leer()

        resultado = []
        for solicitud in datos:
            cumple_legajo = (legajo is None) or (
                solicitud["estudiante"]["legajo"] == legajo
            )
            cumple_estado = (codigo_estado is None) or (
                solicitud["estado"]["codigo"] == codigo_estado
            )
            if cumple_legajo and cumple_estado:
                resultado.append(solicitud)

        self.mostrar(
            f"\n--- RESULTADOS DE BÚSQUEDA (Encontradas: {len(resultado)}) ---"
        )
        for encontrada in resultado:
            self.mostrar(
                f"ID #{encontrada['id_solicitud']} | Legajo: {encontrada['estudiante']['legajo']} ({encontrada['estudiante']['apellido']}, {encontrada['estudiante']['nombre']}) "
                f"| Tipo: {encontrada['tipo']} | Prioridad: {encontrada['prioridad']} | Estado: {encontrada['estado']['codigo']} "
                f"| Área: {encontrada['area_responsable']['nombre_area']}"
            )
        return resultado

    def generar_reporte(self):
        if not self.repositorio.existe():
            self.mostrar("[INFO] No hay datos para generar el reporte.")
            return

        solicitudes = self.repositorio.leer()

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

        self.mostrar("\n=======================================================")
        self.mostrar("       REPORTE GENERAL DE SOLICITUDES ACADÉMICAS       ")
        self.mostrar("=======================================================")
        self.mostrar(f"Total de solicitudes registradas : {len(solicitudes)}")
        self.mostrar(f"  - Pendientes (PEND)            : {pendiente}")
        self.mostrar(f"  - En Revisión (REV)            : {en_revision}")
        self.mostrar(f"  - Aprobadas (APR)              : {aprobada}")
        self.mostrar(f"  - Rechazadas (RECH)            : {rechazada}")
        self.mostrar(f"Solicitudes de prioridad ALTA    : {prioridad_alta}")
        self.mostrar("-------------------------------------------------------")
        self.mostrar("Detalle de solicitudes:")
        for solicitud in solicitudes:
            self.mostrar(
                f"  [#{solicitud['id_solicitud']}] {solicitud['fecha_creacion']} (Vence: {solicitud['fecha_vencimiento']}) - "
                f"{solicitud['estudiante']['apellido']}, {solicitud['estudiante']['nombre']} (Leg: {solicitud['estudiante']['legajo']}) - "
                f"Trámite: {solicitud['tipo']} [{solicitud['estado']['codigo']}] -> {solicitud['area_responsable']['responsable_cargo']}"
            )
        self.mostrar("=======================================================\n")
