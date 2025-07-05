"""Database module."""

from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import logging

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


class DatabaseResource:
    engine_url = '{}://{}:{}@{}:{}/{}'
    def __init__(self, config: dict) -> None:
        db_url = self.engine_url.format(
            config['dialect'],
            config['username'],
            config['password'], 
            config['host'], 
            config['port'], 
            config['db_name']
        )
        self._engine = create_engine(db_url, echo=False,pool_pre_ping=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )


    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()