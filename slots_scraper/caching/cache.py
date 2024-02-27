import pathlib


def store(value: str, key: str) -> None:
    """Store value in a temporary file.

    Saves passed value to a file named `key` in the `/tmp` directory.
    If the file already exists, it gets overridden with the new value.

    Args:
        value (str): The value to store.
        key (str): The name of the file.
    """
    path = _get_cache_filepath(key=key)
    path.write_text(value)


def get(key: str) -> str | None:
    """Retrieve value from a temporary file.

    Returns string content of a file named `key` from the `/tmp` directory.
    If the file does not exist, returns `None`.

    Args:
        key (str): The name of the file to read from.

    Returns:
        The file contents if it exists, `None` otherwise.
    """
    path = _get_cache_filepath(key=key)

    if not path.exists():
        return None

    return path.read_text()


def _get_cache_filepath(key: str) -> pathlib.Path:
    return (pathlib.Path("/tmp") / key).resolve()
