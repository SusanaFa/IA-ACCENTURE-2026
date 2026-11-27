from datetime import datetime
from time import perf_counter

from src import gemini_client


def run_trial() -> None:
    # Tarifas estándar para texto, expresadas por token.
    input_price_per_token = 0.25 / 1_000_000
    output_price_per_token = 1.50 / 1_000_000

    total_queries = 10
    successful_queries = 0
    attempted_queries = 0

    initial_cost = gemini_client.session_cost_usd
    started_at = perf_counter()

    print(f"Inicio: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    print("Modelo: gemini-3.1-flash-lite")
    print(f"Máximo de consultas: {total_queries}")

    for query_number in range(1, total_queries + 1):
        attempted_queries += 1
        print(f"\nConsulta {query_number}:")

        try:
            answer = gemini_client.generate_text(
                f"Prueba {query_number}. Responde únicamente: OK",
                input_price_per_token=input_price_per_token,
                output_price_per_token=output_price_per_token,
            )
        except (ValueError, RuntimeError) as error:
            # Detiene el ensayo ante un fallo definitivo.
            print(f"Ensayo detenido: {error}")
            break

        successful_queries += 1
        print(f"Respuesta: {answer[:80]}")

    trial_cost = gemini_client.session_cost_usd - initial_cost
    elapsed_seconds = perf_counter() - started_at

    print("\nResumen del ensayo")
    print(f"Consultas iniciadas: {attempted_queries}")
    print(f"Consultas exitosas: {successful_queries}")
    print(f"Duración: {elapsed_seconds:.2f} segundos")
    print(f"Costo estimado de entrada y salida: USD {trial_cost:.6f}")


if __name__ == "__main__":
    run_trial()