import json
from datetime import datetime
from pathlib import Path

from src.gemini_client import generate_text
from src.text_pipeline import process_text, reference_word_overlap


CASES = [
    {
        "name": "signature_requirement",
        "question": (
            "Regla del prototipo: la firma del examen es requisito para "
            "cobrar al centro y pagar al médico; no es necesario esperar "
            "su liberación. ¿Qué requisito permite el cobro y el pago?"
        ),
        "reference": "La firma es requisito para el cobro y el pago.",
    },
    {
        "name": "monthly_assignment",
        "question": (
            "En el prototipo aún no se ha confirmado qué fecha determina "
            "la imputación mensual de un examen. "
            "¿Cuál es el estado de esa regla?"
        ),
        "reference": "La fecha de imputación mensual está pendiente de confirmación.",
    },
    {
        "name": "rejected_exam",
        "question": (
            "En el prototipo aún no se ha definido el tratamiento financiero "
            "de los exámenes rechazados. ¿Cuál es el estado de esa regla?"
        ),
        "reference": "El tratamiento financiero de los exámenes rechazados está pendiente de definición.",
    },
]


def run_trial() -> None:
    started_at = datetime.now().astimezone()
    project_root = Path(__file__).resolve().parents[1]

    # Cada ejecución crea una evidencia nueva.
    output_directory = project_root / "docs" / "evidencias"
    output_directory.mkdir(parents=True, exist_ok=True)

    filename = f"pipeline_results_{started_at:%Y%m%d_%H%M%S_%f}.json"
    output_path = output_directory / filename

    report = {
        "started_at": started_at.isoformat(),
        "model": "gemini-3.1-flash-lite",
        "metric": "reference_word_overlap",
        "results": [],
    }

    for case_number, case in enumerate(CASES, start=1):
        print(f"\n[Caso {case_number}] {case['name']}")

        try:
            # Petición real: conserva la respuesta original para la evidencia.
            response = generate_text(
                case["question"],
                system_instruction=(
                    "Responde en español con una sola frase breve, "
                    "sin Markdown y usando únicamente las reglas proporcionadas."
                ),
            )
        except (ValueError, RuntimeError) as error:
            report["results"].append({
                **case,
                "status": "error",
                "error": str(error),
            })
            print(f"Ensayo detenido: {error}")
        else:
            reference_tokens = process_text(case["reference"])
            response_tokens = process_text(response)

            raw_score = reference_word_overlap(
                case["reference"].split(),
                response.split(),
            )
            processed_score = reference_word_overlap(
                reference_tokens,
                response_tokens,
            )

            report["results"].append({
                **case,
                "status": "success",
                "response": response,
                "reference_tokens": reference_tokens,
                "response_tokens": response_tokens,
                "raw_score": raw_score,
                "processed_score": processed_score,
            })

            print(f"Referencia: {case['reference']}")
            print(f"Respuesta: {response}")
            print(f"Coincidencia cruda: {raw_score:.1%}")
            print(f"Coincidencia procesada: {processed_score:.1%}")

        # Guarda también los avances si una consulta posterior falla.
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if report["results"][-1]["status"] == "error":
            break

    successful_cases = sum(
        result["status"] == "success"
        for result in report["results"]
    )
    print(f"\nCasos exitosos: {successful_cases}/{len(CASES)}")
    print(f"Evidencia: {output_path}")


if __name__ == "__main__":
    run_trial()