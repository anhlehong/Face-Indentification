import psycopg2
from psycopg2 import pool
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from config.settings import settings
import atexit


class DatabaseManager:
    def __init__(self):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=settings.DB_MIN_CONN,
            maxconn=settings.DB_MAX_CONN,
            dsn=settings.DB_URL
        )
        atexit.register(self.close)
        self._ensure_extension()

    def _ensure_extension(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    @contextmanager
    def get_connection(self):
        """Quản lý thông minh: Tự mượn, Tự trả, Tự Commit, Tự Rollback"""
        conn = self.pool.getconn()
        try:
            register_vector(conn)
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Database Error: {e}")
            raise e
        finally:
            self.pool.putconn(conn)

    def close(self):
        """Hàm này sẽ tự động chạy khi bác tắt App nhờ atexit"""
        if self.pool:
            self.pool.closeall()
            print("🛑 Pool đã được tự động đóng gọn gàng.")


db_manager = DatabaseManager()
