import re


def clean_text(text: str) -> str:
    """Normaliza mayúsculas, puntuación y espacios."""
    if not isinstance(text, str):
        raise ValueError("El texto debe ser una cadena.")

    normalized_text = text.lower()

    # Conserva caracteres de palabra, incluidas letras con tildes.
    normalized_text = re.sub(r"[^\w\s]", "", normalized_text)

    # Reduce espacios, tabulaciones y saltos de línea a un espacio.
    return re.sub(r"\s+", " ", normalized_text).strip()


def tokenize(cleaned_text: str) -> list[str]:
    """Divide el texto por espacios en blanco."""
    return cleaned_text.split()


def process_text(text: str) -> list[str]:
    """Aplica limpieza y tokenización en ese orden."""
    cleaned_text = clean_text(text)
    return tokenize(cleaned_text)

def reference_word_overlap(
    reference_tokens: list[str],
    response_tokens: list[str],
) -> float:
    """Calcula la proporción de palabras únicas de referencia presentes."""
    reference_words = set(reference_tokens)

    # Evita dividir por cero cuando la referencia no contiene palabras.
    if not reference_words:
        return 0.0

    response_words = set(response_tokens)
    common_words = reference_words & response_words

    return len(common_words) / len(reference_words)