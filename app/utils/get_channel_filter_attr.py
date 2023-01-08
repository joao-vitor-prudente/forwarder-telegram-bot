def get_channel_filter_attr(filter_: str) -> str:
    """Get filter attribute by analyzing it's value.

    Args:
        filter_ (str): value of the filter.

    Returns:
        str: whether the filter is a url or a name.
    """
    
    filter_attr: str = "url" if filter_.startswith("https://") or filter_.startswith("t.me") else "name"
    
    return filter_attr
