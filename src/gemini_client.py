import json
import os
import re

import requests
from dotenv import load_dotenv
from src.retry_client import with_retry

# Carga la configuración local sin incluir credenciales en el código.
load_dotenv()
# Acumulado estimado de esta sesión; se reinicia al iniciar el proceso.
session_cost_usd = 0.0

def build_request(
    question,
    model="gemini-3.1-flash-lite",
    *,
    system_instruction=None,
    response_schema=None,
):
    # Valida la pregunta antes de preparar la petición.
    if not isinstance(question, str):
        raise ValueError("La pregunta debe ser un texto.")

    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    # La instrucción es opcional para conservar las llamadas anteriores.
    if system_instruction is not None:
        if (
            not isinstance(system_instruction, str)
            or not system_instruction.strip()
        ):
            raise ValueError(
                "La instrucción de sistema debe ser un texto no vacío."
            )

    if response_schema is not None:
        if not isinstance(response_schema, dict) or not response_schema:
            raise ValueError(
                "El esquema de respuesta debe ser un diccionario no vacío."
            )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or not api_key.strip():
        raise ValueError("Falta configurar GEMINI_API_KEY en el archivo .env.")

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )
    headers = {"x-goog-api-key": api_key}

    # El contenido cambia en cada petición.
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": question}],
            }
        ]
    }

    # Las instrucciones de comportamiento viajan por separado.
    if system_instruction is not None:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    # Activa la salida estructurada cuando se proporciona un esquema.
    if response_schema is not None:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, headers, payload

def send_request(url, headers, payload):
    # Controla problemas de conexión y de tiempo de espera.
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Gemini no respondió dentro del tiempo de espera."
        ) from None
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "No se pudo conectar con Gemini. Revisa tu conexión."
        ) from None

    # Clasifica los errores HTTP para decidir cuáles se reintentan.
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        status_code = response.status_code

        if status_code in (401, 403):
            # Esperar y repetir no corrige un problema de acceso.
            raise ValueError(
                "Credencial inválida o sin permiso. "
                "Revisa tu GEMINI_API_KEY y sus permisos."
            ) from None

        if status_code == 429:
            # Convención de esta lección: representa el límite de uso.
            raise TimeoutError(
                "Se alcanzó un límite de uso o cuota de Gemini."
            ) from None

        if status_code == 400:
            message = (
                "Gemini rechazó la petición (HTTP 400). "
                "Revisa la clave y el contenido enviado."
            )
        elif status_code >= 500:
            message = (
                f"Gemini no pudo atender la petición (HTTP {status_code}). "
                "Intenta nuevamente más tarde."
            )
        else:
            message = f"La petición falló con el código HTTP {status_code}."

        raise RuntimeError(message) from None

    # Una respuesta HTTP exitosa también debe contener JSON válido.
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(
            "La respuesta de Gemini no contiene JSON válido."
        ) from None

def extract_text(data):
    # Recorre la estructura esperada de la respuesta.
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except KeyError as error:
        raise RuntimeError(
            f"Falta el campo esperado en la respuesta: {error.args[0]}."
        ) from None
    except IndexError:
        raise RuntimeError(
            "La respuesta no contiene candidatos o partes de contenido."
        ) from None
    except TypeError:
        raise RuntimeError(
            "La estructura de la respuesta no tiene el formato esperado."
        ) from None

    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("La respuesta no contiene texto generado válido.")

    return text

def parse_json_response(text, expected_types):
    # Comprueba que exista texto para interpretar.
    if not isinstance(text, str) or not text.strip():
        raise ValueError("La respuesta del modelo está vacía o no es texto.")

    clean_text = text.strip()

    # Retira un bloque Markdown únicamente si envuelve toda la respuesta.
    fenced_block = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```",
        clean_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if fenced_block:
        clean_text = fenced_block.group(1).strip()

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError:
        raise ValueError(
            "La respuesta del modelo no contiene JSON válido."
        ) from None

    # Un JSON válido también podría ser una lista, un número o null.
    if not isinstance(data, dict):
        raise ValueError("La respuesta debe ser un objeto JSON.")

    missing_keys = set(expected_types) - set(data)

    if missing_keys:
        raise ValueError(
            f"Faltan claves requeridas: {', '.join(sorted(missing_keys))}."
        )

    extra_keys = set(data) - set(expected_types)

    if extra_keys:
        raise ValueError(
            f"Hay claves no permitidas: {', '.join(sorted(extra_keys))}."
        )

    # Valida el tipo exacto de cada campo del contrato.
    for key, expected_type in expected_types.items():
        if type(data[key]) is not expected_type:
            raise ValueError(
                f"El campo '{key}' debe ser de tipo "
                f"{expected_type.__name__}."
            )

    return data


def calculate_cost(data, input_price_per_token, output_price_per_token):
    # Lee el consumo informado en la respuesta.
    try:
        usage = data["usageMetadata"]
        input_tokens = usage["promptTokenCount"]
        output_tokens = usage["candidatesTokenCount"]
    except KeyError as error:
        raise RuntimeError(
            f"Falta un dato para calcular el costo: {error.args[0]}."
        ) from None

    # Calcula por separado el costo de entrada y de salida.
    input_cost = input_tokens * input_price_per_token
    output_cost = output_tokens * output_price_per_token

    return input_cost + output_cost

def register_cost(
    data,
    input_price_per_token,
    output_price_per_token,
):
    """Registra una estimación usando tokens de entrada y salida."""
    global session_cost_usd

    # Calcula antes de acumular: si faltan datos, no registra un cero falso.
    operation_cost = calculate_cost(
        data,
        input_price_per_token,
        output_price_per_token,
    )
    session_cost_usd += operation_cost

    print(
        f"Costo estimado de entrada y salida: USD {operation_cost:.6f} "
        f"(acumulado: USD {session_cost_usd:.6f})"
    )

    return operation_cost


def generate_text(
    question,
    *,
    input_price_per_token=None,
    output_price_per_token=None,
):
    # Si se registra costo, deben proporcionarse ambas tarifas.
    if (input_price_per_token is None) != (output_price_per_token is None):
        raise ValueError("Debes proporcionar ambas tarifas por token.")

    url, headers, payload = build_request(question)

    try:
        # Solo se repite el envío; el registro queda fuera del reintento.
        data = with_retry(
            lambda: send_request(url, headers, payload)
        )
    except TimeoutError:
        raise RuntimeError(
            "Se alcanzó un límite de uso o cuota de Gemini "
            "y se agotaron los tres intentos. Intenta más tarde."
        ) from None

    # Registra el consumo informado aunque luego falle la extracción.
    if input_price_per_token is not None:
        register_cost(
            data,
            input_price_per_token,
            output_price_per_token,
        )

    return extract_text(data)


if __name__ == "__main__":
    # Solicita una pregunta cuando se ejecuta este módulo.
    question = input("Escribe tu pregunta: ")

    try:
        result = generate_text(question)
        print(result)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)