import time

from gemini_client import build_request, extract_text, send_request


def compare_models():
    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ]

    # Caso ficticio basado en el propósito del proyecto.
    question = (
        "Actúa como asistente de conciliación de Examia. "
        "Python ya validó un reporte ficticio con 12 exámenes firmados, "
        "3 pendientes de firma y 2 rechazados. "
        "La firma es requisito para cobro y pago; "
        "la fecha de imputación mensual y el tratamiento de rechazados "
        "aún no están definidos. "
        "Redacta un resumen para revisión humana de máximo 100 palabras. "
        "Distingue los hallazgos de las decisiones pendientes. "
        "No inventes importes ni reglas de negocio."
    )

    for model in models:
        latencies = []
        print(f"\nModelo: {model}")

        for attempt in range(4):
            try:
                url, headers, payload = build_request(
                    question,
                    model=model,
                )

                # Mide el envío y la recepción, incluido el procesamiento JSON.
                start = time.perf_counter()
                data = send_request(url, headers, payload)
                elapsed = time.perf_counter() - start

                text = extract_text(data)
                latencies.append(elapsed)

                print(
                    f"Intento {attempt + 1}: "
                    f"{elapsed:.2f} segundos"
                )
                print(f"Respuesta:\n{text}\n")

            except (ValueError, RuntimeError) as error:
                print(f"Intento {attempt + 1} fallido: {error}")

            # Espacia las solicitudes; no garantiza evitar límites de cuota.
            time.sleep(3)

        if latencies:
            average_latency = sum(latencies) / len(latencies)
            print(f"Respuestas válidas: {len(latencies)}/4")
            print(f"Latencia promedio: {average_latency:.2f} segundos")

        if len(latencies) < 4:
            print("Medición incompleta: revisar los intentos fallidos.")


if __name__ == "__main__":
    compare_models()