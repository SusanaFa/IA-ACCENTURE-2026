import time

from gemini_client import build_request, extract_text, send_request


def evaluate_models():
    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ]

    # Casos ficticios: no contienen información de pacientes.
    questions = {
        "monthly_assignment": (
            "Caso ficticio de conciliación Examia. "
            "Un examen ingresó el 31 de octubre y se firmó el 2 de noviembre. "
            "La firma es requisito para cobro y pago, pero aún no se confirma "
            "qué fecha determina la imputación mensual. "
            "¿A qué mes corresponde cobrarlo y pagarlo? "
            "Responde en máximo 80 palabras. "
            "Distingue lo confirmado de lo pendiente y no inventes reglas."
        ),
        "duplicate_records": (
            "Caso ficticio de conciliación Examia. "
            "Python detectó dos registros con el mismo identificador: "
            "en octubre el examen estaba pendiente de firma y en noviembre "
            "aparece firmado. No se ha verificado si fue cobrado o pagado. "
            "Explica el hallazgo y qué debe revisar una persona antes del cierre. "
            "No hay una regla confirmada para eliminar registros automáticamente. "
            "Responde en máximo 80 palabras y no inventes datos ni reglas."
        ),
    }

    for case_name, question in questions.items():
        print(f"\nCaso: {case_name}")

        for model in models:
            print(f"\nModelo: {model}")

            try:
                # Reutiliza el cliente existente para cada caso.
                url, headers, payload = build_request(
                    question,
                    model=model,
                )
                data = send_request(url, headers, payload)
                print(extract_text(data))

            except (ValueError, RuntimeError) as error:
                print("No se pudo evaluar:", error)

            # Espacia las solicitudes.
            time.sleep(3)


if __name__ == "__main__":
    evaluate_models()