from datetime import date

import typer


def validate_date(date_str: str) -> None:
    """
    Validates that a date string is in the correct YYYY-MM-DD format.
    
    Args:
        date_str: The date string to validate (can be any type, will be converted to string)
        
    Raises:
        typer.BadParameter: If the date format is invalid
    """
    try:
        date.fromisoformat(date_str)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid date format: {date_str}. Please use YYYY-MM-DD format."
        )