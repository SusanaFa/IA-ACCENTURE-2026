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

## Alcance actual — Gate 1 y avances M2

Esta versión implementa la base técnica de integración con Gemini y los avances del cliente modular de M2:

- Cliente de la API REST con funciones separadas y `generate_text` como interfaz de consulta de texto.
- Validación de entradas y configuración.
- Manejo de errores de conexión, tiempo de espera, HTTP y formato JSON.
- Clasificación de errores de acceso sin reintentos y de errores HTTP 429 y 500+ con reintentos.
- Espera exponencial con jitter, límite de espera y máximo de intentos.
- Mensaje de error claro al agotarse los intentos.
- Extracción del texto generado.
- Instrucciones de sistema separadas del contenido del usuario mediante `build_request`.
- Solicitud de salida JSON mediante un esquema.
- Interpretación y validación de claves y tipos de la respuesta generada.
- Banco de tres prompts con ejemplos ficticios de Examia.
- Script de consistencia y registro de sus resultados.
- Estimación parcial del costo por tokens de entrada y salida, con registro opcional y acumulado por sesión.
- Registro único de costo después del envío exitoso, fuera del mecanismo de reintento.
- Ensayo de diez consultas reales consecutivas, sin observar un HTTP 429.
- Suite de 17 pruebas automatizadas con mocks, sin llamadas reales a la API ni pausas reales.
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
python -m src.gemini_client
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

`register_cost` reutiliza ese cálculo y acumula la estimación en
`session_cost_usd`. El acumulado se reinicia al iniciar un nuevo proceso.

`generate_text` registra el costo cuando recibe las dos tarifas:
`input_price_per_token` y `output_price_per_token`.
Si se omiten ambas, devuelve el texto sin registrar costo.
Si se proporciona solo una, lanza `ValueError` antes de enviar la petición.

El registro ocurre una sola vez después del envío exitoso,
fuera del mecanismo de reintento. Si se agotan los intentos,
no se registra una estimación para esa consulta.
Si faltan datos de consumo, se informa el error sin alterar el acumulado.

El cálculo no contempla todos los posibles componentes facturables,
como tokens de razonamiento o tarifas de caché.
Es una estimación parcial, no una factura ni una confirmación
del cargo efectivo del proveedor.

## Organización del repositorio

| Ruta                               | Propósito                                                          |
| ---------------------------------- | ------------------------------------------------------------------ |
| `src/gemini_client.py`             | Preparación, envío y procesamiento de peticiones.                  |
| `src/list_models.py`               | Consulta del catálogo de modelos.                                  |
| `src/compare_models.py`            | Medición comparativa de latencia.                                  |
| `src/evaluate_models.py`           | Pruebas de calidad con casos ficticios.                            |
| `prompts/prompt_bank.py`           | Banco de instrucciones, ejemplos y esquemas.                       |
| `prompts/check_consistency.py`     | Ejecución y validación del banco.                                  |
| `prompts/consistency_results.json` | Registro de resultados obtenidos.                                  |
| `docs/architecture_decision.md`    | Comparación y elección del modelo.                                 |
| `docs/miniapp_architecture.png`    | Diagrama de arquitectura.                                          |
| `docs/evidencias/`                 | Capturas de las verificaciones realizadas.                         |
| `.env.example`                     | Plantilla de configuración sin credenciales reales.                |
| `requirements.txt`                 | Dependencias del entorno.                                          |
| `src/retry_client.py`              | Reintento con backoff exponencial, jitter y demostración simulada. |
| `src/rate_limit_trial.py`          | Ensayo acotado de diez consultas reales con costo estimado.        |
| `tests/test_gemini_client.py`      | Pruebas de clasificación HTTP, costos e interfaz pública.          |
| `tests/test_retry_client.py`       | Pruebas de recuperación, pausas y agotamiento de intentos.         |

## Ejecución del ensayo de consultas consecutivas

Desde la raíz del repositorio, con el entorno virtual activo:

```bash
python -m src.rate_limit_trial
```

Realiza hasta diez consultas reales, cada una con hasta tres intentos HTTP.
Puede generar cargos y se detiene ante el primer error definitivo.
No garantiza que se alcance un límite de uso.

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

## Ensayo de consultas consecutivas — M2

- Modelo: gemini-3.1-flash-lite.
- Nivel del proyecto: Tier 1.
- Límite mostrado: 4.000 solicitudes por minuto.
- Consultas iniciadas: 10.
- Consultas exitosas: 10.
- Duración: 16,16 segundos.
- Costo estimado de entrada y salida: USD 0,000043.
- Reintentos observados: ninguno.
- HTTP 429: no observado durante este ensayo.

Las consultas reales y el registro de costos funcionaron.
El backoff, el agotamiento de intentos y la ausencia de
registros de costo ante fallos se comprobaron mediante simulaciones.

Este ensayo no demuestra recuperación ante un HTTP 429 real.
El costo informado es una estimación parcial, no un cargo
confirmado en la facturación del proveedor.

## Pruebas unitarias del cliente modular — M2

Ejecutar desde la raíz, con el entorno virtual activo:

```bash
python -m pytest tests/test_gemini_client.py tests/test_retry_client.py -v
```

Resultado observado: 17 passed in 0.40s.

Cobertura de escenarios:

- Clasificación HTTP: 401, 403, 429, 400, 500 y 503.
- Respuesta JSON exitosa.
- Recuperación mediante reintentos y espera exponencial con jitter.
- Propagación inmediata de errores no reintentables.
- Agotamiento de intentos.
- Cálculo y acumulación del costo estimado.
- Registro único de costo tras recuperarse de fallos.
- Ausencia de registro de costo al agotarse los intentos.
- Conversión del error final y propagación del error de acceso.

Las pruebas utilizan mocks para el envío HTTP y las pausas,
tarifas ficticias y un fixture que aísla el acumulado de costos.
No requieren una API key real.

En esta versión, HTTP 429 y HTTP 500+ producen TimeoutError
como convención interna para activar el reintento.

Estas pruebas no demuestran recuperación ante un HTTP 429 real.
