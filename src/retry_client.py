import time
from typing import Any, Callable
import random

def with_retry(
    operation: Callable[[], Any],
    attempts: int = 3,
    delay_seconds: float = 2,
    max_delay_seconds: float = 30,
) -> Any:
    """Reintenta con espera exponencial y variación aleatoria."""
    if attempts < 1:
        raise ValueError("Debe existir al menos un intento.")

    if delay_seconds < 0 or max_delay_seconds < 0:
        raise ValueError("Las esperas no pueden ser negativas.")

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except TimeoutError:
            if attempt == attempts:
                raise

            # Duplica la espera base con cada nuevo reintento.
            delay = min(
                delay_seconds * (2 ** (attempt - 1)),
                max_delay_seconds,
            )

            # Agrega hasta un 10 % de variación sin superar el máximo.
            delay_with_jitter = min(
                delay + random.uniform(0, delay * 0.1),
                max_delay_seconds,
            )

            print(
                f"Intento {attempt} de {attempts} falló por límite "
                f"de uso o error del servidor. "
                f"Reintentando en {delay_with_jitter:.1f}s..."
            )
            time.sleep(delay_with_jitter)


def run_demo() -> None:
    """Simula dos fallos y una respuesta exitosa."""
    previous_attempts = 0

    def mock_request() -> dict:
        nonlocal previous_attempts
        previous_attempts += 1

        # Para esta lección, TimeoutError representa un límite de uso.
        if previous_attempts < 3:
            raise TimeoutError("Límite de peticiones excedido.")

        return {
            "content": "Respuesta simulada exitosa",
            "attempt": previous_attempts,
        }

    response = with_retry(mock_request)
    print(response)

if __name__ == "__main__":
    run_demo()