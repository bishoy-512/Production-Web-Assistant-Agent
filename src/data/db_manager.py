import os
from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config.settings import Environment, settings
from system.logs import logger


class DatabaseManager:

    def __init__(self):
        connection_url = (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        try:
            self.db_engine = create_async_engine(
                connection_url,
                pool_pre_ping=True,
                pool_size=settings.POSTGRES_POOL_SIZE,
                max_overflow=settings.POSTGRES_MAX_OVERFLOW,
                pool_timeout=30,
                pool_recycle=1800,
                echo=settings.DEBUG,
            )

            self.session_factory = async_sessionmaker(
                self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        except SQLAlchemyError as e:
            logger.error(
                "database_engine_creation_failed",
                error=str(e),
                environment=str(settings.APP_ENV),
            )
            if settings.APP_ENV != Environment.PRODUCTION:
                raise

    async def check_connection(self):
        try:
            async with self.db_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        except Exception:
            logger.critical("database_connection_failed")
            raise

    async def get_db_session(self):
        async with self.session_factory() as db_session:
            try:
                yield db_session
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise

    async def dispose(self) -> None:
        await self.db_engine.dispose()


db_manager = DatabaseManager()


def main():
    """Entry Point for the Program."""
    print(f"Welcome from `{os.path.basename(__file__).split('.')[0]}` Module. Nothing to do ^_____^!")


if __name__ == "__main__":
    main()