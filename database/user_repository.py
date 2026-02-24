from database.postgres import db_manager
from entities.user import User
from config.settings import settings


class UserRepository:
    def __init__(self):
        self.db = db_manager
        self.setup_table()

    def setup_table(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(50) PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        embedding vector({settings.EMBEDDING_DIM})
                    );
                """)
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS face_idx ON users USING hnsw (embedding vector_cosine_ops);")

    def add_user(self, user: User):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (id, full_name, embedding) VALUES (%s, %s, %s) RETURNING id;",
                    (user.id, user.full_name, user.embedding.tolist())
                )
                return cur.fetchone()[0]

    def search_face(self, embedding, threshold=settings.FACE_MATCH_THRESHOLD):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                sql = """
                    SELECT id, full_name, 1 - (embedding <=> %s::vector) AS similarity 
                    FROM users
                    WHERE 1 - (embedding <=> %s::vector) > %s 
                    ORDER BY similarity DESC LIMIT 1;
                """
                cur.execute(sql, (embedding.tolist(),
                            embedding.tolist(), threshold))
                res = cur.fetchone()
                return {"id": res[0], "name": res[1], "similarity": res[2]} if res else None

    def delete_all(self):
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE users;")


user_repo = UserRepository()
