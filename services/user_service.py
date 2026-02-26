import json
import cv2
import numpy as np
import logging
from pathlib import Path
from core.engine import face_engine
from database.user_repository import user_repo
from entities.user import User
from config.settings import settings
from services.base import BaseService
from services.face_service import face_service

logger = logging.getLogger(__name__)


class UserService(BaseService):

    def __init__(self):
        super().__init__()
        self.face_service = face_service

    def create_from_json(self, json_path: str):
        path = Path(json_path)
        if not path.exists():
            logger.error(f"❌ File JSON không tồn tại: {json_path}")
            return

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            u_id, u_name = entry.get('id'), entry.get('name')
            u_images = entry.get('images')
            if isinstance(u_images, str):
                u_images = [u_images]

            embeddings = []
            for img_p in u_images:
                emb = self.face_service.extract_embedding(img_p)
                if emb is not None:
                    embeddings.append(emb)

            if not embeddings:
                logger.warning(f"⚠️ Bỏ qua {u_name}: Không tìm thấy mặt.")
                continue

            # Tính vector trung bình và chuẩn hóa (Mean Embedding)
            final_emb = np.mean(embeddings, axis=0)
            final_emb = final_emb / np.linalg.norm(final_emb)

            user = User(full_name=u_name, id=u_id, embedding=final_emb)
            self.repo.add_user(user)
            logger.info(f"✅ Đã nạp: {u_name} ({len(embeddings)} ảnh)")

    def search_face_by_embedding(self, embedding, threshold: float = None):
        """
        Tìm kiếm thông tin người dựa trên vector embedding có sẵn.
        """
        if threshold is None:
            threshold = settings.FACE_MATCH_THRESHOLD

        match = self.repo.search_face(embedding, threshold=threshold)

        if match:
            return {
                "id": match["id"],
                "name": match["name"],
                "similarity": match.get("similarity", 0.0)
            }

        return {
            "id": None,
            "name": "Unknown",
            "similarity": 0.0
        }


user_service = UserService()
