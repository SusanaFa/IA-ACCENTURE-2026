from unittest.mock import Mock, patch
from src import gemini_client

import pytest
import requests

from src.gemini_client import send_request

@pytest.fixture(autouse=True)
def reset_session_cost(monkeypatch):
    """Cada prueba empieza en cero y al finalizar restaura el valor previo."""
    monkeypatch.setattr(gemini_client, "session_cost_usd", 0.0)



@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (401, ValueError),
        (403, ValueError),
        (429, TimeoutError),
        (500, TimeoutError),
        (503, TimeoutError),
        (400, RuntimeError),
    ],
)


def test_send_request_classifies_http_errors(status_code, expected_error):
    """Comprueba la clasificación usando respuestas HTTP simuladas."""
    response = Mock()
    response.status_code = status_code

    # El código real llama a raise_for_status para detectar el rechazo.
    response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=response
    )

    with patch(
        "src.gemini_client.requests.post",
        return_value=response,
    ) as mock_post:
        with pytest.raises(expected_error):
            send_request(
                "https://example.invalid",
                {"x-goog-api-key": "fake-key"},
                {"contents": []},
            )

    mock_post.assert_called_once()
    response.json.assert_not_called()


def test_send_request_returns_json_on_success():
    """Una petición exitosa devuelve el JSON sin transformarlo."""
    expected_data = {
        "candidates": [
            {"content": {"parts": [{"text": "Respuesta simulada"}]}}
        ]
    }

    response = Mock()
    response.status_code = 200
    response.raise_for_status.return_value = None
    response.json.return_value = expected_data

    with patch(
        "src.gemini_client.requests.post",
        return_value=response,
    ):
        result = send_request(
            "https://example.invalid",
            {"x-goog-api-key": "fake-key"},
            {"contents": []},
        )

    assert result == expected_data
    response.json.assert_called_once_with()

def test_register_cost_calculates_and_accumulates():
    """Calcula entrada y salida y acumula dos operaciones."""
    data = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
        }
    }

    # Tarifas ficticias para verificar la fórmula.
    input_price = 0.00000010
    output_price = 0.00000040

    first_cost = gemini_client.register_cost(
        data, input_price, output_price
    )

    assert first_cost == pytest.approx(0.000213)
    assert gemini_client.session_cost_usd == pytest.approx(0.000213)

    second_cost = gemini_client.register_cost(
        data, input_price, output_price
    )

    assert second_cost == pytest.approx(0.000213)
    assert gemini_client.session_cost_usd == pytest.approx(0.000426)


def test_register_cost_preserves_total_when_usage_is_incomplete():
    """Si faltan datos de consumo, falla sin alterar el acumulado."""
    gemini_client.session_cost_usd = 0.001
    data = {
        "usageMetadata": {
            "promptTokenCount": 850,
            # Falta candidatesTokenCount.
        }
    }

    with pytest.raises(RuntimeError, match="candidatesTokenCount"):
        gemini_client.register_cost(
            data,
            0.00000010,
            0.00000040,
        )

    assert gemini_client.session_cost_usd == pytest.approx(0.001)

def test_generate_text_recovers_and_registers_cost_once(monkeypatch):
    """Dos fallos y un éxito generan un único registro de costo."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    data = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
        },
        "candidates": [
            {"content": {"parts": [{"text": "Respuesta simulada"}]}}
        ],
    }

    with (
        patch(
            "src.gemini_client.send_request",
            side_effect=[
                TimeoutError("Primer fallo"),
                TimeoutError("Segundo fallo"),
                data,
            ],
        ) as mock_send,
        patch("src.retry_client.time.sleep") as mock_sleep,
        patch(
            "src.gemini_client.register_cost",
            wraps=gemini_client.register_cost,
        ) as mock_register,
    ):
        result = gemini_client.generate_text(
            "Pregunta de prueba",
            input_price_per_token=0.00000010,
            output_price_per_token=0.00000040,
        )

    assert result == "Respuesta simulada"
    assert mock_send.call_count == 3
    assert mock_sleep.call_count == 2
    mock_register.assert_called_once_with(
        data, 0.00000010, 0.00000040
    )
    assert gemini_client.session_cost_usd == pytest.approx(0.000213)


def test_generate_text_converts_exhausted_retries_without_cost(monkeypatch):
    """El agotamiento produce RuntimeError sin registrar costo."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    with (
        patch(
            "src.gemini_client.send_request",
            side_effect=TimeoutError("Fallo temporal"),
        ) as mock_send,
        patch("src.retry_client.time.sleep") as mock_sleep,
        patch("src.gemini_client.register_cost") as mock_register,
    ):
        with pytest.raises(RuntimeError, match="tras tres intentos"):
            gemini_client.generate_text(
                "Pregunta de prueba",
                input_price_per_token=0.00000010,
                output_price_per_token=0.00000040,
            )

    assert mock_send.call_count == 3
    assert mock_sleep.call_count == 2
    mock_register.assert_not_called()
    assert gemini_client.session_cost_usd == 0.0


def test_generate_text_propagates_access_error_without_retry(monkeypatch):
    """Conserva el error de acceso sin repetir ni registrar costo."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
    original_error = ValueError("Credencial inválida o sin permiso.")

    with (
        patch(
            "src.gemini_client.send_request",
            side_effect=original_error,
        ) as mock_send,
        patch("src.retry_client.time.sleep") as mock_sleep,
        patch("src.gemini_client.register_cost") as mock_register,
    ):
        with pytest.raises(ValueError) as captured:
            gemini_client.generate_text(
                "Pregunta de prueba",
                input_price_per_token=0.00000010,
                output_price_per_token=0.00000040,
            )

    assert captured.value is original_error
    mock_send.assert_called_once()
    mock_sleep.assert_not_called()
    mock_register.assert_not_called()
    assert gemini_client.session_cost_usd == 0.0