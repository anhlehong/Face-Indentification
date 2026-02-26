from database.user_repository import user_repo
from core.engine import face_engine


class BaseService:
    def __init__(self):
        self.engine = face_engine
        self.repo = user_repo
