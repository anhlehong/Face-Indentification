import psycopg2
from psycopg2 import pool
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from config.settings import settings
import atexit
import sys


class DatabaseManager:
    def __init__(self):
        try:
            conn_url = settings.DB_URL
            separator = "&" if "?" in conn_url else "?"
            full_url = f"{conn_url}{separator}connect_timeout=5"

            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=settings.DB_MIN_CONN,
                maxconn=settings.DB_MAX_CONN,
                dsn=full_url
            )
            self._ensure_extension()
            atexit.register(self.close)
            print("🚀 DatabaseManager: Khởi tạo thành công.")
        except Exception as e:
            print(f"❌ DatabaseManager: Không thể khởi tạo Pool. Lỗi: {e}")
            sys.exit(1)

    def _ensure_extension(self):
        """Cài đặt pgvector bằng một kết nối riêng biệt, không dùng register_vector ở đây"""
        conn = self.pool.getconn()
        try:
            conn.autocommit = True  # Cần thiết để chạy CREATE EXTENSION
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ DatabaseManager: Extension 'vector' đã sẵn sàng.")
        except Exception as e:
            print(f"❌ DatabaseManager: Lỗi khi cài extension: {e}")
            raise e
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def get_connection(self):
        """Quản lý kết nối: Tự mượn, Tự trả, Tự Commit/Rollback"""
        conn = self.pool.getconn()
        try:
            # Đăng ký kiểu dữ liệu vector cho kết nối này
            register_vector(conn)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database Error: {e}")
            raise e
        finally:
            self.pool.putconn(conn)

    def close(self):
        if self.pool:
            self.pool.closeall()
            print("🛑 DatabaseManager: Đã đóng toàn bộ kết nối.")


db_manager = DatabaseManager()
