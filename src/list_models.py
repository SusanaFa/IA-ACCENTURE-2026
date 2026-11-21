import os

import requests
from dotenv import load_dotenv


load_dotenv()


def list_models():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or not api_key.strip():
        raise ValueError("Falta configurar GEMINI_API_KEY en .env.")

    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {"x-goog-api-key": api_key}
    params = {"pageSize": 1000}

    while True:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,
        )

        # Evita mostrar información de la petición al informar un error.
        if not response.ok:
            raise RuntimeError(
                f"No se pudo consultar el catálogo: HTTP {response.status_code}."
            )

        data = response.json()

        for model in data.get("models", []):
            methods = model.get("supportedGenerationMethods", [])

            if "generateContent" in methods:
                print(model["name"].removeprefix("models/"))

        # Consulta la página siguiente si el catálogo continúa.
        next_page = data.get("nextPageToken")

        if not next_page:
            break

        params["pageToken"] = next_page


if __name__ == "__main__":
    try:
        list_models()
    except requests.exceptions.JSONDecodeError:
        print("El servicio no devolvió JSON válido.")
    except requests.exceptions.RequestException:
        print("No se pudo consultar el servicio. Revisa tu conexión.")
    except (ValueError, RuntimeError) as error:
        print(error)