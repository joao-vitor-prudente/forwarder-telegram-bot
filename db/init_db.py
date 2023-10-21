from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from classes.fatal_exceptions import ConnectionException
from classes.sqlalchemy_protocols import EngineProtocol, SessionProtocol


def init_db(connection_str: str) -> tuple[EngineProtocol, SessionProtocol] | Exception:

    """ Initialize database connection and session.
    :param connection_str_: connection string.
    :return: engine_ and session sqlalchemy objects.
    """
    
    try:
        engine: Engine = create_engine(connection_str)
        session: Session = sessionmaker()(bind=engine)
    except SQLAlchemyError as e:
        return ConnectionException(connection_str=connection_str, exc=e)
    
    return engine, session
