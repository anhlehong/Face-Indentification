import logging
from services.face_service import face_service
from services.user_service import user_service

logger = logging.getLogger(__name__)


class IdentityService:
    def __init__(self):
        self.face_svc = face_service
        self.user_svc = user_service

    # Xử lý AI sau mỗi 3 khung hình
        self.process_interval = 3
        self.frame_count = 0
        self.cached_results = []

    def process_frame(self, frame):
        """
        Nhận frame từ CameraService, trả về kết quả định danh đầy đủ.
        """
        self.frame_count += 1

        if self.frame_count % self.process_interval == 0:
            new_results = []
            faces = self.face_svc.detect_one_face(frame)

            for face in faces:
                user_info = self.user_svc.search_face_by_embedding(
                    face.embedding)

                # BƯỚC 3: Đóng gói dữ liệu chuẩn (Bbox, Kps, Identity)
                result = {
                    "bbox": face.bbox.astype(int).tolist(),  # [x1, y1, x2, y2]
                    "kps": face.kps.astype(int).tolist() if hasattr(face, 'kps') else [],
                    "name": user_info["name"],
                    "id": user_info["id"],
                    "similarity": user_info.get("similarity", 0),
                    "color": (0, 255, 0) if user_info["id"] else (0, 0, 255)
                }
                new_results.append(result)

            self.cached_results = new_results
            self.frame_count = 0  # Reset counter

        return self.cached_results


identity_service = IdentityService()
