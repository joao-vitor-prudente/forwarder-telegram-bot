from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, BigInteger  # type: ignore
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# many-to-many relationship table between channels.
input_output = Table(
    "InputOutput",
    Base.metadata,
    Column("id", Integer(), primary_key=True, autoincrement=True),
    Column("input_id", Integer(), ForeignKey("Channel.id")),
    Column("output_id", Integer(), ForeignKey("Channel.id")),
)


class Channel(Base):
    __tablename__ = "Channel"

    id = Column("id", String(), primary_key=True)
    name = Column("name", String(), nullable=False, unique=True)
    url = Column("url", String(), nullable=False, unique=True)

    # TODO: THIS MANY TO MANY WITH IT SELF RELATIONSHIP MAY BE SUBOPTIMAL
    inputs = relationship(
        "Channel",
        secondary=input_output,
        primaryjoin=id == input_output.c.output_id,  # type: ignore
        secondaryjoin=id == input_output.c.input_id,  # type: ignore
        back_populates="outputs"
    )
    outputs = relationship(
        "Channel",
        secondary=input_output,
        primaryjoin=id == input_output.c.input_id,  # type: ignore
        secondaryjoin=id == input_output.c.output_id,  # type: ignore
        back_populates="inputs",
        overlaps="inputs"
    )

    def __repr__(self) -> str:
        return f"Channel(name={self.name}, url={self.url})"
    

class Log(Base):    
    __tablename__ = "Log"

    id = Column(String(), primary_key=True)
    date = Column(DateTime(), nullable=False)
    message = Column(String(), nullable=False)

    def __repr__(self) -> str:
        return f"Log(date={self.date}, message={self.message})"


class Admin(Base):
    __tablename__ = "Admin"

    id = Column(String(), primary_key=True)
    login = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False, unique=True)
    authorized_chat_id = Column(BigInteger(), unique=True)

    def __repr__(self) -> str:
        return f"Admin(login={self.login}, password={self.password}, token_id={self.authorized_chat_id})"


class Filter(Base):
    __tablename__ = "Filter"
    
    id = Column(String(), primary_key=True)
    condition = Column(String(), nullable=False, unique=True)
    replacement = Column(String(), nullable=True)
    mode = Column(String(), nullable=False)