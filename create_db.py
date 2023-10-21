import pymysql
pymysql.install_as_MySQLdb()

from bcrypt import hashpw

from argparse import ArgumentParser

from uuid import uuid4

from app.utils.env import get_env_var, load_env

from db.init_db import init_db
from db.schema import Admin, Base

from classes.sqlalchemy_protocols import SessionProtocol, EngineProtocol

from classes.validation_exceptions import InvalidEnvironmentException


def configure_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog = "create_db",
        description = "Creates the database using the information on the .env file.",
        epilog = ""
    )
    parser.add_argument("env", type=str, help="Environment to load. [dev or prod]")
    return parser


def main() -> None | Exception:
    connection_str: str = get_env_var("DATABASE_URL")
    
    db: tuple[EngineProtocol, SessionProtocol] | Exception = init_db(connection_str)
    if isinstance(db, Exception): return db
    engine, session = db
    
    Base.metadata.create_all(engine)
    
    admins: list[Admin] = session.query(Admin).all()
    
    if len(admins) > 0:
        return
    
    pw_: str | Exception = get_env_var("ADMIN_PASSWORD")
    salt_: str | Exception = get_env_var("SALT")
    login: str | Exception = get_env_var("ADMIN_LOGIN")
    
    if isinstance(pw_, Exception): return pw_
    if isinstance(salt_, Exception): return salt_
    if isinstance(login, Exception): return login
    
    pw: bytes = pw_.encode()
    salt: bytes = salt_.encode()
    
    h_pw: str = hashpw(pw, salt).decode()
    
    session.add(Admin(id=str(uuid4()), login=login, password=h_pw))
    session.commit()  # type: ignore


if __name__ == "__main__":
    parser: ArgumentParser = configure_parser()
    args = parser.parse_args()
    if args.env in ["dev", "prod"]:
        load_env(args.env)
        main()
    else:
        raise InvalidEnvironmentException(env=args.env)