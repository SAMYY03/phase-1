def add(a: int, b: int) -> int:
    """Return the sum of two numbers."""
    return a + b


def determine_path(level: str) -> str:
    """Determine AI learning path based on level."""
    if level == "Beginner":
        return "Python & basics"
    return "Advanced AI"
