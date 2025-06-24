import contextlib
import threading
import logging
from typing import Optional, Dict, Any, AsyncGenerator, AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncConnection,
)
from sqlalchemy.orm import DeclarativeBase
from config import Config


logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}


_thread_local = threading.local()

class DatabaseSessionManager:
    def __init__(self, db_url: str, engine_kwargs: Optional[Dict[str, Any]] = None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(db_url, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    async def close(self):
        if not self._engine:
            raise RuntimeError("DatabaseSessionManager engine is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_thread_local_session_manager() -> DatabaseSessionManager:
    """
    Retrieve or create a thread-local instance of DatabaseSessionManager.
    """
    if not hasattr(_thread_local, "session_manager"):
        _thread_local.session_manager = DatabaseSessionManager(
            Config.DB_URL,
            engine_kwargs={
                "echo": True if logger.isEnabledFor(logging.DEBUG) else False,
                "future": True,
                "execution_options": {"isolation_level": "AUTOCOMMIT"},
            },
        )
    return _thread_local.session_manager

async def get_db_session():
    session_manager = get_thread_local_session_manager()
    async with session_manager.session() as session:
        yield session
