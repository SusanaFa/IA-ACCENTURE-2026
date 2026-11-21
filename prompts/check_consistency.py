import json
import time
from datetime import datetime, timezone
from pathlib import Path

from prompts.prompt_bank import PROMPT_BANK
from src.gemini_client import (
    build_request,
    extract_text,
    parse_json_response,
    send_request,
)


MODEL = "gemini-3.1-flash-lite"
REPETITIONS = 3
PAUSE_SECONDS = 3


def check_consistency():
    # Guarda los resultados junto al script, independientemente de la consola.
    output_path = Path(__file__).resolve().parent / "consistency_results.json"

    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "repetitions_per_prompt": REPETITIONS,
        "validation_scope": "JSON object, exact keys and field types",
        "prompts": {},
    }

    for prompt in PROMPT_BANK:
        attempts = []
        successes = 0

        print(f"\nPrompt: {prompt['name']}")

        for attempt in range(1, REPETITIONS + 1):
            attempt_result = {
                "attempt": attempt,
                "valid": False,
                "raw_text": None,
            }

            try:
                url, headers, payload = build_request(
                    prompt["user_example"],
                    model=MODEL,
                    system_instruction=prompt["system_instruction"],
                    response_schema=prompt["response_schema"],
                )

                response_data = send_request(url, headers, payload)
                text = extract_text(response_data)

                # Conserva el texto incluso si luego falla la validación.
                attempt_result["raw_text"] = text

                parsed_data = parse_json_response(
                    text,
                    prompt["expected_types"],
                )

                attempt_result["valid"] = True
                attempt_result["parsed_data"] = parsed_data
                successes += 1

                print(f"  Intento {attempt}: estructura válida")

            except (ValueError, RuntimeError) as error:
                attempt_result["error"] = str(error)
                print(f"  Intento {attempt}: falló — {error}")

            attempts.append(attempt_result)

            # Espacia las solicitudes; no elimina los límites de cuota.
            time.sleep(PAUSE_SECONDS)

        report["prompts"][prompt["name"]] = {
            "successes": successes,
            "failures": REPETITIONS - successes,
            "attempts": attempts,
        }

        # Guarda al terminar cada prompt para conservar el avance.
        with output_path.open("w", encoding="utf-8") as output_file:
            json.dump(report, output_file, indent=2, ensure_ascii=False)

        print(f"Resultado: {successes}/{REPETITIONS} respuestas válidas")

    print(f"\nRegistro guardado en: {output_path}")


if __name__ == "__main__":
    check_consistency()