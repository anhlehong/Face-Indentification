import json
import cv2
import numpy as np
import logging
from pathlib import Path
from core.engine import face_engine
from database.user_repository import user_repo
from entities.user import User
from config.settings import settings

logger = logging.getLogger(__name__)


class IdentityService:
    def __init__(self):
        self.engine = face_engine
        self.repo = user_repo

    def _get_embedding_from_path(self, img_path: str):
        """Helper: Đọc ảnh và lấy embedding mặt chính diện nhất"""
        frame = cv2.imread(img_path)
        if frame is None:
            logger.error(f"❌ Không thể đọc ảnh: {img_path}")
            return None

        faces = self.engine.detect_and_extract(frame)
        return faces[0].embedding if faces else None

    def register_from_json(self, json_path: str):
        """Đăng ký hàng loạt từ file JSON (Hỗ trợ 1 hoặc nhiều ảnh mỗi người)"""
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
                emb = self._get_embedding_from_path(img_p)
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

    def search_face_by_path(self, img_path: str, threshold: float = None):
        """
        Tìm kiếm người trong ảnh dựa trên đường dẫn.
        Trả về danh sách kết quả cho TẤT CẢ khuôn mặt tìm thấy trong ảnh.
        """
        if threshold is None:
            threshold = settings.FACE_MATCH_THRESHOLD

        frame = cv2.imread(img_path)
        if frame is None:
            logger.error(f"❌ Không thể mở ảnh để search: {img_path}")
            return []

        faces = self.engine.detect_and_extract(frame)
        results = []

        for face in faces:
            # So khớp vector với Postgres (Cosine Similarity)
            match = self.repo.search_face(face.embedding, threshold=threshold)

            if match:
                results.append({
                    "id": match["id"],
                    "name": match["name"],
                    "similarity": match["similarity"],
                    "box": face.bbox.tolist()  # Tọa độ khung mặt để vẽ nếu cần
                })
            else:
                results.append({
                    "id": None,
                    "name": "Unknown",
                    "similarity": 0.0,
                    "box": face.bbox.tolist()
                })

        return results


identity_service = IdentityService()
