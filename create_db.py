from bcrypt import hashpw

from uuid import uuid4

from app.utils.env import get_env_var, load_env

from db.init_db import init_db
from db.schema import Admin, Base

from classes.sqlalchemy_protocols import SessionProtocol, EngineProtocol



def main() -> None | Exception:
    connection_str: str = "sqlite:///database.db"
    
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
    load_env("dev")
    main()