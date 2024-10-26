from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_PORT, DB_NAME, DB_PASS, DB_USER, DB_HOST
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание DSN (Data Source Name) для подключения к базе данных PostgreSQL
DSN = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Создание движка SQLAlchemy
engine = create_engine(DSN)

# Настройка сессии с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Контекстный менеджер для получения сессии базы данных.
    Закрывает сессию после завершения работы.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
