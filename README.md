# Sistema de Gestión de Solicitudes Académicas — TPI Metodología de Sistemas II

Trabajo Práctico Integrador de la asignatura **Metodología de Sistemas II** (Tecnicatura Universitaria en Programación a Distancia - UTN).

Este proyecto aborda la evolución profesional de un sistema de software existente, partiendo de una versión base funcional (`estado-inicial`) para diagnosticar su deuda técnica y *code smells*, aplicar principios **SOLID** y **Clean Code**, ejecutar *refactorings* seguros y verificar mediante pruebas y *Code Review* que el comportamiento externo se mantiene intacto (`estado-refactorizado`).

---

## 📋 Descripción del Dominio y Alcance

El sistema modela un módulo académico-administrativo universitario que permite registrar, validar, clasificar, derivar y dar seguimiento a solicitudes académicas realizadas por estudiantes (equivalencias, certificados, excepciones de correlatividad y bajas).

### Entidades Principales
* **`Estudiante`**: Representa al alumno solicitante con sus datos identificatorios y su situación académica (`REG`, `LIBRE`, `EGR` y cantidad de materias aprobadas).
* **`Estado`**: Representa la situación del expediente dentro de su ciclo de vida (`PEND`, `REV`, `APR`, `RECH`).
* **`ResponsableArea`**: Representa el departamento institucional y el responsable asignado al trámite.
* **`Solicitud`**: Entidad central que vincula al estudiante, el tipo y prioridad del pedido, el área asignada, el estado actual y los plazos de vencimiento.

*(Ver el diagrama de clases inicial en [UML_inicial.md](./UML_inicial.md)).*

---

## ⚙️ Funcionalidades Implementadas

El sistema cuenta con **5 operaciones funcionales verificables**:
1. **Registrar solicitud académica**: Valida campos obligatorios, formato de legajo e email, verifica la regularidad del estudiante según el tipo de trámite, asigna automáticamente el área responsable, calcula la fecha de vencimiento según la prioridad y persiste el trámite.
2. **Cambiar estado de una solicitud**: Actualiza el estado del trámite (`PEND` -> `REV` -> `APR` / `RECH`), registrando observaciones y validando que no se reabran expedientes ya finalizados.
3. **Asignar / Reasignar responsable**: Permite derivar una solicitud a una nueva área administrativa o autoridad académica.
4. **Buscar y filtrar solicitudes**: Consulta de expedientes filtrando por número de legajo del estudiante y/o código de estado.
5. **Generar reporte general**: Emite un resumen estadístico por consola con totales por estado, cantidad de trámites de prioridad alta y el detalle completo de solicitudes registradas.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje**: Python 3.10+ (Biblioteca estándar: `json`, `os`, `datetime`, sin dependencias externas).
* **Persistencia**: Almacenamiento estructurado en archivo local JSON (`solicitudes_db.json`).
* **Control de versiones**: Git y GitHub con trazabilidad por etapas mediante *tags*.

---

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd TPI_Metodologia_II
   ```

2. **Ejecutar la aplicación por consola:**
   ```bash
   python src/main.py
   ```

3. **Modo de Demostración Automática (Verificación de comportamiento externo):**
   Al iniciar el menú interactivo en consola, seleccione la **Opción `6` (`Ejecutar escenario de demostración completo`)**. Esta opción ejecuta un lote reproducible de pruebas sobre las 5 operaciones (incluyendo casos válidos y rechazos por reglas de negocio) y actualiza el archivo `solicitudes_db.json`.

---

## 🏷️ Trazabilidad del Proyecto (Tags Obligatorios)

| Tag de Git | Etapa del TPI | Descripción del Hito |
| :--- | :--- | :--- |
| `estado-inicial` | Etapa 1 y 2 | Entrega del sistema base funcional con deuda técnica inicial para diagnóstico. |
| `etapa-diagnostico` | Etapa 3 | Documentación del análisis de calidad interna y detección de *code smells*. |
| `etapa-refactoring` | Etapas 4 y 5 | Aplicación de principios SOLID, Clean Code y refactorings seguros. |
| `etapa-pruebas` | Etapa 6 | Casos de prueba y verificación comparativa del comportamiento antes/después. |
| `etapa-docs` | Etapa 7 | Checklist de *Code Review* profesional y documentación técnica en `/docs`. |
| `estado-refactorizado` | Entrega Final | Versión final mejorada, revisada y con comportamiento externo verificado. |

---

## 👥 Integrantes del Equipo
