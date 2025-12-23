def validate_deck_name(name: str) -> bool:
    """Validate deck name - no special characters"""
    if not name or not name.strip():
        return False

    # Проверяем на недопустимые символы
    invalid_chars = ["/", "\\", "?", "%", "#"]
    return not any(char in name for char in invalid_chars)


def sanitize_text(text: str) -> str:
    """Sanitize text for Telegram HTML"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text
