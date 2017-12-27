import re
import base64


def snake_case(string):
    """Convert string into snake case.
    Join punctuation with underscore
    Args:
        string: String to convert.
    Returns:
        string: Snake cased string.
    """

    string = re.sub(r"[\-\.\s]", '_', str(string))
    if not string:
        return string
    return string[0].lower() + re.sub(
        r"[A-Z]",
        lambda matched: '_' + matched.group(0).lower(),
        string[1:]
    )


def camel_case(string):
    """ Convert string into camel case.
    Args:
        string: String to convert.
    Returns:
        string: Camel case string.
    """

    string = re.sub(r"^[\-_\.]", '', str(string))
    if not string:
        return string
    return string[0].lower() + re.sub(
        r"[\-_\.\s]([a-z])",
        lambda matched: matched.group(1).upper(),
        string[1:]
    )


def b64encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


def b64decode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.b64decode(data).decode()
