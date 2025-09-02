from types import TracebackType
from typing import Self, Type

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from vidaplus.settings import Settings


class DatabaseConnectionHandler:
    def __init__(self) -> None:
        self.__connection_string = Settings().DATABASE_URL
        self.__engine = self.__create_engine()

    def __create_engine(self) -> Engine:
        return create_engine(self.__connection_string)

    def __enter__(self) -> Self:
        sessionmake = sessionmaker(bind=self.__engine)
        self.session = sessionmake()
        return self

    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        self.session.close()
