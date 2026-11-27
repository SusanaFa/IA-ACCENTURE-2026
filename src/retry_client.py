import time
from typing import Any, Callable


def with_retry(
    operation: Callable[[], Any],
    attempts: int = 3,
    delay_seconds: float = 2,
) -> Any:
    """Ejecuta una operación y reintenta solo ante TimeoutError."""
    if attempts < 1:
        raise ValueError("Debe existir al menos un intento.")

    if delay_seconds < 0:
        raise ValueError("La espera no puede ser negativa.")

    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except TimeoutError:
            # En el último intento, propaga el error sin otra espera.
            if attempt == attempts:
                raise

            print(
                f"Intento {attempt} de {attempts} falló por límite "
                f"de uso. Reintentando en {delay_seconds} segundos..."
            )
            time.sleep(delay_seconds)


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