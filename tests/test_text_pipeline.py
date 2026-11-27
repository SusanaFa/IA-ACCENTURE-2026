import pytest

from src.text_pipeline import process_text, reference_word_overlap
from src.text_pipeline import process_text


def test_process_text_normalizes_case_and_punctuation():
    """Las diferencias de formato no alteran las palabras."""
    result = process_text("El Cielo, es AZUL!")

    assert result == ["el", "cielo", "es", "azul"]


@pytest.mark.parametrize("text", ["", "   \t\n", "¡¡¡...!!!"])
def test_process_text_returns_empty_list_for_empty_content(text):
    """Un texto sin palabras produce una lista vacía."""
    assert process_text(text) == []


def test_process_text_preserves_spanish_letters_and_normalizes_spaces():
    """Conserva tildes y ñ, y normaliza espacios en blanco."""
    result = process_text("  MÉDICO\t informó:\nMAÑANA.  ")

    assert result == ["médico", "informó", "mañana"]


def test_process_text_rejects_non_string_input():
    """Rechaza entradas que no representan texto."""
    with pytest.raises(ValueError, match="cadena"):
        process_text(None)

def test_reference_word_overlap_changes_after_normalization():
    """La normalización corrige diferencias de mayúsculas y puntuación."""
    reference = "El cielo es azul."
    response = "el cielo es azul"

    raw_score = reference_word_overlap(
        reference.split(),
        response.split(),
    )
    processed_score = reference_word_overlap(
        process_text(reference),
        process_text(response),
    )

    assert raw_score == pytest.approx(0.5)
    assert processed_score == pytest.approx(1.0)


def test_reference_word_overlap_handles_empty_reference():
    """Una referencia vacía produce cero, sin división por cero."""
    assert reference_word_overlap([], ["respuesta"]) == 0.0


def test_reference_word_overlap_ignores_word_order():
    """Documenta que la métrica no distingue quién realiza la acción."""
    reference = process_text("El perro persiguió al gato.")
    response = process_text("El gato persiguió al perro.")

    assert reference_word_overlap(reference, response) == 1.0


def test_reference_word_overlap_ignores_repetitions():
    """Documenta que repetir palabras no cambia la coincidencia."""
    reference = process_text("El gato")
    response = process_text("El gato el gato")

    assert reference_word_overlap(reference, response) == 1.0