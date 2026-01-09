# database_manager.py
import pyodbc
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.engine = self._create_engine()

    def _create_engine(self):
        server = self.config.get('server')
        db = self.config.get('database')
        user = self.config.get('user')
        pwd = self.config.get('password')
        driver = self.config.get('driver')

        if not all([server, db, user, pwd, driver]):
            logger.error("❌ ERROR: Una o más variables en el .env no fueron encontradas.")

        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={db};"
            f"UID={user};"
            f"PWD={pwd};"
        )

        def creator():
            return pyodbc.connect(conn_str, timeout=10)

        return create_engine("mssql+pyodbc://", creator=creator)
        # 3. Le decimos a SQLAlchemy que use esa función para conectar
        # Esto evita que SQLAlchemy intente "parsear" o modificar tu cadena

    def execute_query(self, query, params=None):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error de base de datos: {e}")
            raise