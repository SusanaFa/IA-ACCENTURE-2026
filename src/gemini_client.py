import os

import requests
from dotenv import load_dotenv

# Cargando/leyendo las variables del archivo .env.
load_dotenv()


def generate_text(question):
    # Lectura de la clave sin escribirla dentro del código.
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-3.5-flash-lite"

    # Equivale a la URL y los headers usados en Thunder Client.
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )
    headers = {"x-goog-api-key": api_key}

    # Un diccionario de Python que requests enviará como JSON.
    payload = {
        "contents": [
            {"parts": [{"text": question}]}
        ]
    }

    # Envía la petición y limita la espera a 30 segundos.
    response = requests.post(
        url, headers=headers, json=payload, timeout=30
    )
    response.raise_for_status()

    # Convierte el JSON recibido en estructuras de Python.
    data = response.json()

    # Devuelve únicamente el texto generado.
    return data["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    result = generate_text(
        "Responde únicamente: Conexión con Gemini exitosa."
    )
    print(result)