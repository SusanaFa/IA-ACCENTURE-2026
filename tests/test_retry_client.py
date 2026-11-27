from unittest.mock import Mock, patch

import pytest

from src.retry_client import with_retry


def test_with_retry_returns_immediate_success():
    """Si funciona a la primera, no repite ni espera."""
    operation = Mock(return_value="ok")

    with patch("src.retry_client.time.sleep") as mock_sleep:
        result = with_retry(operation)

    assert result == "ok"
    operation.assert_called_once_with()
    mock_sleep.assert_not_called()


def test_with_retry_recovers_after_temporary_errors():
    """Dos fallos temporales generan dos pausas antes del éxito."""
    operation = Mock(
        side_effect=[
            TimeoutError("Primer fallo"),
            TimeoutError("Segundo fallo"),
            "ok",
        ]
    )

    with patch("src.retry_client.time.sleep") as mock_sleep:
        result = with_retry(operation, attempts=3)

    assert result == "ok"
    assert operation.call_count == 3
    assert mock_sleep.call_count == 2

    # Comprueba los rangos sin exigir un valor aleatorio exacto.
    first_delay = mock_sleep.call_args_list[0].args[0]
    second_delay = mock_sleep.call_args_list[1].args[0]

    assert 2 <= first_delay <= 2.2
    assert 4 <= second_delay <= 4.4


@pytest.mark.parametrize("error_type", [ValueError, RuntimeError])
def test_with_retry_does_not_retry_other_errors(error_type):
    """Los errores ajenos a TimeoutError se propagan inmediatamente."""
    original_error = error_type("Error no reintentable")
    operation = Mock(side_effect=original_error)

    with patch("src.retry_client.time.sleep") as mock_sleep:
        with pytest.raises(error_type) as captured:
            with_retry(operation)

    assert captured.value is original_error
    operation.assert_called_once_with()
    mock_sleep.assert_not_called()


def test_with_retry_propagates_last_error_when_attempts_exhausted():
    """Al agotar intentos, propaga el último error sin otra pausa."""
    last_error = TimeoutError("Último fallo")
    operation = Mock(
        side_effect=[
            TimeoutError("Primer fallo"),
            TimeoutError("Segundo fallo"),
            last_error,
        ]
    )

    with patch("src.retry_client.time.sleep") as mock_sleep:
        with pytest.raises(TimeoutError) as captured:
            with_retry(operation, attempts=3)

    assert captured.value is last_error
    assert operation.call_count == 3
    assert mock_sleep.call_count == 2