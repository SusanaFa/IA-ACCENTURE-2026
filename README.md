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

## Alcance actual — Gate 1

Esta versión implementa la base técnica de integración con Gemini:

- Cliente de la API REST con funciones separadas.
- Validación de entradas y configuración.
- Manejo de errores de conexión, tiempo de espera, HTTP y formato JSON.
- Extracción del texto generado.
- Instrucciones de sistema separadas del contenido del usuario.
- Solicitud de salida JSON mediante un esquema.
- Interpretación y validación de claves y tipos de la respuesta generada.
- Banco de tres prompts con ejemplos ficticios de Examia.
- Script de consistencia y registro de sus resultados.
- Función de estimación de costo por tokens, probada por separado.
- Comparación de modelos y decisión de arquitectura documentada.

La lectura de reportes, la conciliación automática y el cálculo de cobros
y pagos todavía no están implementados.

## Reglas de negocio iniciales

- El período mensual comprende desde el día 1 hasta el último día del mes.
- La firma del examen es requisito para cobro a centros y pago médico;
  no se requiere esperar su liberación.
- La fecha que determinará la imputación mensual está pendiente de confirmación.
- El tratamiento de los exámenes rechazados está pendiente de definición.
- Los casos sin una regla confirmada deben quedar señalados para revisión.

## Uso de inteligencia artificial

La IA apoya la explicación de hallazgos y la elaboración de resúmenes.

Las validaciones y los cálculos financieros se implementarán en Python
mediante reglas explícitas previamente confirmadas.
La aprobación de cobros y pagos corresponderá a una persona.

## Requisitos

- Git instalado.
- Python 3.14 utilizado durante el desarrollo en Windows.
- Acceso a internet.
- Una clave propia de Gemini API con acceso y cuota para
  `gemini-3.1-flash-lite`.

Las dependencias también se instalaron sin conflictos en una comprobación
adicional con Python 3.12 en Linux. Esa comprobación no sustituye el ensayo
completo de instalación y ejecución en Windows.

Las instrucciones siguientes corresponden a Windows con Git Bash.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/SusanaFa/IA-ACCENTURE-2026.git
cd IA-ACCENTURE-2026
```

Si el repositorio es privado, se necesita acceso autorizado para clonarlo.

### 2. Crear y activar el entorno virtual

```bash
py -m venv venv
source venv/Scripts/activate
```

La terminal debería mostrar `(venv)`.

Los comandos siguientes utilizan `python` dentro del entorno activado.

### 3. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
python -m pip check
```

La segunda instrucción comprueba si existen conflictos entre dependencias.

### 4. Configurar la credencial

```bash
cp .env.example .env
```

Abrir `.env` en un editor y reemplazar el valor de ejemplo de
`GEMINI_API_KEY` por una clave propia.

El archivo debe quedar en la raíz del proyecto.
No publicar la clave en código, capturas, registros ni commits.

La variable necesaria para el funcionamiento actual es:

```dotenv
GEMINI_API_KEY=YOUR_API_KEY
```

## Ejecución del cliente de texto

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python src/gemini_client.py
```

El programa solicita una pregunta. Para comprobar la conexión se puede escribir:

```text
Responde únicamente: Conexión con Gemini exitosa.
```

La ejecución correcta muestra una respuesta real del modelo.
El texto puede variar.

Este modo devuelve texto libre; no activa por defecto las instrucciones
ni el esquema del banco de prompts.

## Ejecución del banco de prompts

Desde la raíz del repositorio:

```bash
python -m prompts.check_consistency
```

El script ejecuta tres repeticiones de cada uno de estos prompts:

- `monthly_assignment`: imputación mensual sin regla confirmada.
- `status_change_review`: seguimiento de un examen entre períodos.
- `rejected_exam_review`: tratamiento pendiente de exámenes rechazados.

Cada petición utiliza instrucciones de sistema y un esquema de salida.
La respuesta debe contener exactamente:

| Campo             | Tipo    | Contenido                      |
| ----------------- | ------- | ------------------------------ |
| `summary`         | string  | Resumen en español.            |
| `requires_review` | boolean | Indicación de revisión humana. |

El script verifica que la respuesta sea un objeto JSON y comprueba sus
claves y tipos.

Los resultados se guardan en:

```text
prompts/consistency_results.json
```

Cada ejecución realiza nueve peticiones reales y reemplaza el registro
anterior. Requiere acceso y cuota disponibles.

El resultado guardado del 21 de noviembre de 2026 fue:

| Prompt                 | Respuestas válidas | Fallidas |
| ---------------------- | -----------------: | -------: |
| `monthly_assignment`   |                3/3 |        0 |
| `status_change_review` |                3/3 |        0 |
| `rejected_exam_review` |                3/3 |        0 |

Estos resultados demuestran consistencia estructural en esa corrida.
La corrección del contenido requiere revisión adicional; el script no
comprueba automáticamente las reglas de negocio ni el máximo de palabras.

## Modelo seleccionado

Proveedor: Google Gemini API.

Modelo predeterminado: `gemini-3.1-flash-lite`.

Se comparó con `gemini-3.5-flash-lite` mediante mediciones de latencia
y preguntas ficticias representativas de Examia.

La elección, los precios consultados, los resultados y las limitaciones
están en la [decisión de arquitectura](docs/architecture_decision.md).

## Estimación de costo

`calculate_cost` utiliza `promptTokenCount` y `candidatesTokenCount`
de `usageMetadata`, junto con precios por token proporcionados como parámetros.

Actualmente se prueba por separado y no se ejecuta dentro de `generate_text`.

El cálculo no contempla todos los posibles componentes facturables,
como tokens de razonamiento o tarifas de caché. No debe interpretarse
como una factura ni como el cobro efectivo de una petición gratuita.

## Organización del repositorio

| Ruta                               | Propósito                                           |
| ---------------------------------- | --------------------------------------------------- |
| `src/gemini_client.py`             | Preparación, envío y procesamiento de peticiones.   |
| `src/list_models.py`               | Consulta del catálogo de modelos.                   |
| `src/compare_models.py`            | Medición comparativa de latencia.                   |
| `src/evaluate_models.py`           | Pruebas de calidad con casos ficticios.             |
| `prompts/prompt_bank.py`           | Banco de instrucciones, ejemplos y esquemas.        |
| `prompts/check_consistency.py`     | Ejecución y validación del banco.                   |
| `prompts/consistency_results.json` | Registro de resultados obtenidos.                   |
| `docs/architecture_decision.md`    | Comparación y elección del modelo.                  |
| `docs/miniapp_architecture.png`    | Diagrama de arquitectura.                           |
| `docs/evidencias/`                 | Capturas de las verificaciones realizadas.          |
| `.env.example`                     | Plantilla de configuración sin credenciales reales. |
| `requirements.txt`                 | Dependencias del entorno.                           |

## Manejo de errores

El cliente controla:

- Preguntas vacías o de tipo incorrecto.
- Clave ausente.
- Instrucciones o esquemas con formato de entrada inválido.
- Errores de conexión y tiempo de espera.
- Respuestas HTTP de error, incluidos problemas de acceso y cuota.
- Respuestas HTTP que no contienen JSON válido.
- Campos o elementos faltantes al extraer el texto.
- Texto generado que no puede interpretarse como un objeto JSON.
- Claves faltantes, adicionales o con tipos incorrectos.

Un mensaje de error controlado permite entender la falla, pero no cuenta
como una petición exitosa para verificar el Gate 1.

## Datos y credenciales

Los ejemplos utilizados son ficticios.
No se incluyen reportes reales ni datos personales de pacientes.

`.gitignore` excluye `.env`, los entornos virtuales y los archivos
temporales de Python. `.env.example` contiene únicamente valores de ejemplo.

## Registro del ensayo de instalación limpia

- Fecha: 2026-11-24.
- Entorno: Windows, Git Bash y Python 3.14.7.
- Copia independiente: `gate1-clean-check`.
- Dependencias instaladas mediante `python -m pip install -r requirements.txt`.
- Verificación: `python -m pip check` no detectó conflictos.
- Ejecución: el cliente recibió una respuesta real de Gemini:
  “Instalación limpia de Examia verificada”.
- Seguridad: `.env` y `venv/` están ignorados; `.env` no está versionado.
- La copia de prueba quedó sin cambios pendientes en Git.

Se observó un HTTP 400 en el primer intento debido a que no se encontraba la API_KEY correcta. Las ejecuciones posteriores
fueron exitosas.

Evidencias:

- [Ejecución y seguridad](docs/evidencias/gate1-clean-install.png)
- [Python y dependencias](docs/evidencias/gate1-dependencies-check.png)

El ensayo se realizó en una carpeta y un entorno virtual nuevos del mismo
computador; no equivale a una prueba en otro equipo.
