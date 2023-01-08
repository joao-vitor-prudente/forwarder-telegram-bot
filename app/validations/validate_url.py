def validate_url(url: str) -> bool:
    """Validates the url by checking if it points to the correct channel.

    Args:
        url (str): url to a telegram channel.

    Returns:
        bool: True if the url is valid, False otherwise.
    """

    return url.startswith("https://t.me/")
