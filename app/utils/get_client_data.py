from dataclasses import dataclass

from app.utils.env import get_env_var, load_env

from classes.validation_exceptions import EnvironmentVariableException


@dataclass
class ClientData:
    api_id: int
    api_hash: str
    phone: str
    url: str


def get_client_data(env: str) -> ClientData | Exception:
    """Gets data from the environment variables required to initialize the client.

    Args:
        env (str): environment to load [dev or prod].

    Returns:
        ClientData | Exception: dataclass contianing all necessary data to initialize the client or exception if any.
    """
    
    load_env(env)
    api_id: str | Exception = get_env_var("API_ID")
    api_hash: str | Exception = get_env_var("API_HASH")
    phone: str | Exception = get_env_var("PHONE")
    url: str | Exception = get_env_var("BOT_URL")

    if isinstance(api_id, Exception): return api_id
    if isinstance(api_hash, Exception): return api_hash
    if isinstance(phone, Exception): return phone
    if isinstance(url, Exception): return url
    
    if not api_id.isdigit(): return EnvironmentVariableException(message="API_ID must be an integer", var_name="API_ID")

    api_id_: int = int(api_id)
    
    client_data = ClientData(api_id_, api_hash, phone, url)
    
    return client_data
