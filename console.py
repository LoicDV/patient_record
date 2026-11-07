import re
from collections.abc import Callable, Collection, Sequence
from datetime import date, datetime
from typing import Any

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
MAX_COLUMN_WIDTH = 40

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\+?[\d\s().-]{6,20}$")

Validator = Callable[[str], str | None]

def validate_email(value: str) -> str | None:
    """Check that value looks like an email address

    Args:
        value (str): Text entered by the user

    Returns:
        str | None: An error message if the email is invalid,
            None if it is valid
    """
    return None if EMAIL_PATTERN.match(value) else "Invalid email address."

def validate_phone(value: str) -> str | None:
    """Check that value looks like a phone number.

    Accepts digits, spaces, dots, dashes, parentheses and a leading '+',
    between 6 and 20 characters.

    Args:
        value (str): Text entered by the user

    Returns:
        str | None: An error message if the phone number is invalid,
            None if it is valid
    """
    return None if PHONE_PATTERN.match(value) else "Invalid phone number."

def ask_text(
    message: str,
    *,
    required: bool = True,
    max_length: int | None = None,
    default: str | None = None,
    validator: Validator | None = None,
) -> str | None:
    """Ask for a line of text until it is valid.

    Args:
        message (str): Question displayed to the user
        required (bool): Refuse an empty answer when there is no default
        max_length (int | None): Maximum number of characters
        default (str | None): Value returned for an empty answer
        validator (Validator | None): Extra check returning an error message

    Returns:
        str | None: The answer, the default, or None for an empty optional field
    """
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{message}{suffix}: ").strip()
        if not value:
            if default is not None or not required:
                return default
            print("This field is required.")
        elif max_length is not None and len(value) > max_length:
            print(f"Maximum {max_length} characters.")
        elif validator is not None and (error := validator(value)):
            print(error)
        else:
            return value

def ask_int(
    message: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Ask for an integer within optional bounds

    Args:
        message (str): Question displayed to the user
        min_value (int | None, optional): Minimal value the user needs to enter
            Defaults to None
        max_value (int | None, optional): Maximal value the user needs to enter
            Defaults to None

    Returns:
        int: The number the user enters
    """
    while True:
        raw = input(f"{message}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if min_value is not None and value < min_value:
            print(f"The value must be at least {min_value}.")
        elif max_value is not None and value > max_value:
            print(f"The value must be at most {max_value}.")
        else:
            return value

def ask_id(message: str, valid_ids: Collection[int]) -> int | None:
    """Ask for one of the IDs displayed in a list, until a valid one is entered

    Args:
        message (str): Question displayed to the user
        valid_ids (Collection[int]): IDs the user is allowed to choose

    Returns:
        int | None: The chosen ID, or None if the user typed 0 to cancel
    """
    while True:
        value = ask_int(f"{message} (0 to cancel)", min_value=0)
        if value == 0:
            return None
        if value in valid_ids:
            return value
        print("This ID is not in the list above.")

def ask_date(message: str, *, default: date | None = None, allow_future: bool = True) -> date:
    """Ask for a date in YYYY-MM-DD format, until it is valid

    Args:
        message (str): Question displayed to the user
        default (date | None, optional): Value returned for an empty answer
            Defaults to None
        allow_future (bool, optional): Accept dates after today
            Defaults to True

    Returns:
        date: The date entered, or the default for an empty answer
    """
    suffix = f" [{default.isoformat()}]" if default else ""
    while True:
        raw = input(f"{message} (YYYY-MM-DD){suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            value = datetime.strptime(raw, DATE_FORMAT).date()
        except ValueError:
            print("Invalid date, expected format: YYYY-MM-DD.")
            continue
        if not allow_future and value > date.today():
            print("The date cannot be in the future.")
        else:
            return value

def ask_datetime(message: str) -> datetime:
    """Ask for a date and time in YYYY-MM-DD HH:MM format, empty for now

    Args:
        message (str): Question displayed to the user

    Returns:
        datetime: The date entered, or the current time (without seconds)
            for an empty answer
    """
    while True:
        raw = input(f"{message} (YYYY-MM-DD HH:MM, empty for now): ").strip()
        if not raw:
            return datetime.now().replace(second=0, microsecond=0)
        try:
            return datetime.strptime(raw, DATETIME_FORMAT)
        except ValueError:
            print("Invalid date, expected format: YYYY-MM-DD HH:MM.")

def ask_choice(message: str, choices: Sequence[str], *, default: str | None = None) -> str:
    """Ask for one value among choices

    Args:
        message (str): Question displayed to the user
        choices (Sequence[str]): Accepted values, case-insensitively
        default (str | None, optional): Value returned for an empty answer
            Defaults to None

    Returns:
        str: The chosen value
    """
    options = "/".join(choices)
    suffix = f" [{default}]" if default else ""
    by_lower = {choice.lower(): choice for choice in choices}
    while True:
        raw = input(f"{message} ({options}){suffix}: ").strip().lower()
        if not raw and default is not None:
            return default
        if raw in by_lower:
            return by_lower[raw]
        print(f"Please answer one of: {options}.")

def ask_confirmation(message: str) -> bool:
    """Ask a yes/no question. Anything other than 'y' or 'yes' means no

    Args:
        message (str): Message for the user for the confirmation

    Returns:
        bool: True if the user answered 'y' or 'yes', False otherwise
    """
    return input(f"{message} [y/N]: ").strip().lower() in ("y", "yes")

def print_title(title: str) -> None:
    """Print a section title

    Args:
        title (str): Title of the section
    """
    print(f"\n=== {title} ===")

def format_value(value: Any) -> str:
    """Convert a database value to display text

    Args:
        value (Any): Value to format

    Returns:
        str: Text adapted to the type of value ('-' for None)
    """
    if value is None:
        return "-"
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone()  # show times in the local time zone
        return value.strftime(DATETIME_FORMAT)
    if isinstance(value, date):
        return value.isoformat()
    return str(value)

def truncate(text: str, width: int = MAX_COLUMN_WIDTH) -> str:
    """Shorten text to width characters, ending with '...' if cut

    Args:
        text (str): Text to shorten
        width (int, optional): Maximum length of the result
            Defaults to MAX_COLUMN_WIDTH

    Returns:
        str: The text unchanged if short enough,
            otherwise cut and ending with '...'
    """
    return text if len(text) <= width else text[: width - 3] + "..."

def print_table(rows: Sequence[dict[str, Any]],
                columns: Sequence[tuple[str, str]]) -> None:
    """Print rows as an aligned text table

    Args:
        rows: Rows returned by the database, as dictionaries
        columns: (key, header) pairs, in display order
    """
    if not rows:
        print("No results.")
        return

    cells = [
        [truncate(format_value(row[key])) for key, _ in columns] for row in rows
        ]
    headers = [header for _, header in columns]
    widths = [
        max(len(header), *(len(line[i]) for line in cells)) for i, header in enumerate(headers)
        ]

    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)).rstrip())
    print("  ".join("-" * width for width in widths))
    for line in cells:
        print("  ".join(cell.ljust(width) for cell, width in zip(line, widths)).rstrip())