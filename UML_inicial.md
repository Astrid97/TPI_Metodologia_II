# Diagrama de Clases UML - Sistema Base (`estado-inicial`)

Este diagrama representa la estructura inicial del **Sistema de Gestión de Solicitudes Académicas** antes del proceso de refactoring.

```mermaid
classDiagram
    class Estudiante {
        +String nombre
        +String apellido
        +int legajo
        +String dni
        +String email
        +String condicion
        +int materias_aprobadas
    }

    class Estado {
        +String codigo
        +String descripcion
        +String fecha_actualizacion
    }

    class ResponsableArea {
        +String nombre_area
        +String responsable_cargo
        +String email_contacto
    }

    class Solicitud {
        +int id_solicitud
        +Estudiante estudiante
        +String tipo
        +String prioridad
        +String descripcion
        +String fecha_creacion
        +Estado estado
        +ResponsableArea area_responsable
        +int dias_vencimiento
        +validar_legajo_y_regularidad_estudiante() Tuple~bool, String~
    }

    class GestorSolicitudesAcademicas {
        +String archivo_db
        +procesar_solicitud(id_solicitud, nombre_est, apellido_est, legajo_est, dni_est, email_est, condicion_est, materias_aprobadas, tipo_solicitud, prioridad, descripcion, fecha_str) bool
        +cambiar_estado(id_solicitud, nuevo_codigo_estado, observacion, fecha_actualizacion) bool
        +asignar_responsable(id_solicitud, nueva_area, nuevo_responsable, nuevo_email) bool
        +buscar_solicitudes(legajo, codigo_estado) List~dict~
        +generar_reporte() void
    }

    Solicitud *-- "1" Estudiante : contiene
    Solicitud *-- "1" Estado : tiene
    Solicitud *-- "1" ResponsableArea : asignada a
    GestorSolicitudesAcademicas ..> Solicitud : instancia y procesa
    GestorSolicitudesAcademicas ..> Estudiante : instancia
    GestorSolicitudesAcademicas ..> Estado : instancia
    GestorSolicitudesAcademicas ..> ResponsableArea : instancia
```

## Descripción de Entidades Iniciales
- **`Estudiante`**: Datos personales y condición académica del alumno solicitante (`REG`, `LIBRE`, `EGR`).
- **`Estado`**: Estado actual del trámite (`PEND`, `REV`, `APR`, `RECH`), observación y fecha de último cambio.
- **`ResponsableArea`**: Sector institucional y autoridad asignada para la resolución del expediente.
- **`Solicitud`**: Entidad principal que agrupa al estudiante, el estado, el área responsable y los plazos del trámite.
- **`GestorSolicitudesAcademicas`**: Clase encargada de procesar las operaciones del sistema y gestionar la persistencia en `solicitudes_db.json`.