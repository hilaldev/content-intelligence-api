def enforce_char_limit(text: str, limit: int) -> str:
    """
    Trims text to limit, ensuring it doesn't cut off mid-word.
    """
    if len(text) <= limit:
        return text
    
    truncated = text[:limit]
    # Backtrack to the last space to avoid cutting a word
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    
    return truncated + "..."