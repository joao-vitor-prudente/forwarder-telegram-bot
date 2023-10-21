from dotenv import load_dotenv  # type: ignore
from os import getenv

from classes.validation_exceptions import EnvironmentVariableException


def load_env(env_name: str) -> None:
        
    """ Loads the correct environment.
    :param: env_name: string containing environment name (dev or prod).
    :return: None.
    """
    
    if env_name == "dev":
        load_dotenv("dev.env")
    elif env_name == "prod":
        load_dotenv("prod.env")


def get_env_var(var_name: str) -> str | Exception:

    """ Get environment variable value.
    :param var_name: string containing key in .env file.
    :return: string containing value of key.
    """
    
    env_var: str | None = getenv(var_name)
    # get all environment variables

    if env_var is None:
        print(var_name)
        return EnvironmentVariableException(var_name=var_name)
    
    return env_var
