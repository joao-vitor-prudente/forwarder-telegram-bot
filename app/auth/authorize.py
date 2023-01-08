from sqlalchemy.exc import SQLAlchemyError

import bcrypt

from db.schema import Admin

from classes.fatal_exceptions import DatabaseQueryException
from classes.sqlalchemy_protocols import SessionProtocol

def authorize(login: str, password: str, session: SessionProtocol) -> bool | Exception:
    """Check if the login and password coresponds to any admin user in the database.

    Args:
        login (str): login username.
        password (str): password to be hashed and compared.
        session (SessionProtocol): sqlalchemy session instance.

    Returns:
        bool | Exception: true if the username and password belong to an admin and false otherwize, or exception if any.
    """

    try:
        admin: Admin = session.query(Admin).filter(Admin.login == login).first()  # type: ignore
    except SQLAlchemyError as e:
        return DatabaseQueryException(exc=e)
    
    if admin is None:
        return False

    if not bcrypt.checkpw(bytes(password, encoding="utf-8"), bytes(str(admin.password), encoding="utf-8")):
        return False

    return True

