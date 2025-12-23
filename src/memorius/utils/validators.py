def validate_deck_name(name: str) -> bool:
    """Validate deck name - no special characters"""
    if not name or not name.strip():
        return False

    # Проверяем на недопустимые символы
    invalid_chars = ["/", "\\", "?", "%", "#"]
    return not any(char in name for char in invalid_chars)
