# Examia — Asistente de conciliación mensual con IA

Proyecto de aprendizaje desarrollado durante la Especialización en
Inteligencia Artificial de Skillnest / Accenture 2026.

Autora: Susana Farías.

## Problema de negocio

Examia necesita revisar sus reportes mensuales de exámenes para determinar
qué corresponde cobrar a los centros médicos y pagar a los médicos informantes.

La fecha de ingreso de un examen puede ser distinta de su fecha de firma.
Además, los reportes muestran el estado del examen al momento de descargarlos.
Esto hace necesario revisar los cambios entre períodos para evitar omisiones
y cobros o pagos duplicados.

## Objetivo

Desarrollar una herramienta en Python que apoye la conciliación mensual
de exámenes y utilice IA generativa para explicar los resultados y preparar
resúmenes para revisión humana.

## Alcance previsto

- Leer y validar reportes descargados de Examia.
- Identificar exámenes repetidos y datos incompletos.
- Comparar registros entre períodos.
- Aplicar reglas de cobro y pago previamente confirmadas.
- Generar un resumen de resultados y casos que requieren revisión.

El desarrollo será progresivo, de acuerdo con las actividades y los gates
del programa.

## Reglas de negocio iniciales

- El período mensual comprende desde el día 1 hasta el último día del mes.
- El criterio acordado para cobro a centros y pago médico es la firma del examen;
  no se requiere esperar su liberación.
- La fecha que determinará la imputación mensual está pendiente de confirmación.
- El tratamiento de los exámenes rechazados está pendiente de definición.
- Los casos sin una regla confirmada deben quedar señalados para revisión.

## Uso de inteligencia artificial

Python realizará las validaciones y los cálculos mediante reglas explícitas.

La IA generativa apoyará la explicación de hallazgos y la elaboración de
resúmenes. La aprobación de cobros y pagos corresponderá a una persona.

## Datos y credenciales

Durante el aprendizaje se utilizarán datos ficticios, identificados como tales.

No se incluirán datos personales de pacientes, reportes reales ni credenciales
en este repositorio. Las claves de API se configurarán mediante variables
de entorno y quedarán excluidas del control de versiones.

## Estado actual

Unidad U1.3: cliente de Gemini implementado en `src/gemini_client.py`.

El módulo separa la preparación de la petición, el envío y la extracción
del texto. Valida la entrada y la configuración de la clave, y gestiona
errores de conexión, tiempo de espera, estado HTTP, JSON inválido y
datos faltantes.

Verificación realizada:

- Clave inválida, pregunta vacía y respuesta real exitosa.
- Simulación de errores de conexión, JSON inválido y datos faltantes.

Las evidencias están en `docs/evidencias/`.

La conciliación de reportes de Examia sigue pendiente de implementación.

## Instalación y ejecución

Desde Git Bash, en la raíz del repositorio:

1. Crear el entorno: `py -m venv venv`
2. Activarlo: `source venv/Scripts/activate`
3. Instalar dependencias: `python -m pip install -r requirements.txt`
4. Copiar la configuración: `cp .env.example .env`
5. Completar `GEMINI_API_KEY` en `.env` con una clave propia.
6. Ejecutar: `python src/gemini_client.py`

Proveedor utilizado: Google Gemini.
Modelo probado: `gemini-3.5-flash-lite`.

## Tecnologías previstas

- Python.
- Git y GitHub.
- API de un proveedor de IA generativa, por seleccionar.

Las dependencias y las instrucciones de instalación se documentarán
cuando se configure el entorno de desarrollo.
