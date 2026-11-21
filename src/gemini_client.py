import os

import requests
from dotenv import load_dotenv

# Carga la configuración local sin incluir credenciales en el código.
load_dotenv()


def build_request(question):
    # Valida la entrada antes de preparar o enviar una petición.
    if not isinstance(question, str):
        raise ValueError("La pregunta debe ser un texto.")

    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or not api_key.strip():
        raise ValueError("Falta configurar GEMINI_API_KEY en el archivo .env.")

    model = "gemini-3.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )
    headers = {"x-goog-api-key": api_key}
    payload = {
        "contents": [
            {"parts": [{"text": question}]}
        ]
    }

    return url, headers, payload


def send_request(url, headers, payload):
    # Controla los errores que pueden ocurrir al contactar al servicio.
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

    # Distingue un rechazo HTTP de un problema de conexión.
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        status_code = response.status_code

        if status_code in (401, 403):
            message = "Gemini rechazó el acceso. Revisa la clave y sus permisos."
        elif status_code == 400:
            message = (
                "Gemini rechazó la petición (HTTP 400). "
                "Revisa la clave y el contenido enviado."
            )
        elif status_code == 429:
            message = "Se alcanzó un límite de uso o cuota de Gemini."
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



def generate_text(question):
    # Coordina el proceso y entrega el resultado.
    url, headers, payload = build_request(question)
    data = send_request(url, headers, payload)
    return extract_text(data)


if __name__ == "__main__":
    # La consola presenta los errores controlados al usuario.
    question = input("Escribe tu pregunta: ")

    try:
        result = generate_text(question)
        print(result)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)