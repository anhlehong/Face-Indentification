import cv2
import logging
import numpy as np
from pathlib import Path
import onnxruntime as ort

logger = logging.getLogger(__name__)


class AntiSpoofService:
    def __init__(self):
        self.model_path = "models/anti_spoofing.onnx"  # Đường dẫn model thật sau này
        self.is_active = False
        self.session = None

        # Tự động nạp model nếu file tồn tại
        if Path(self.model_path).exists():
            try:
                self.session = ort.InferenceSession(
                    self.model_path, providers=['CPUExecutionProvider'])
                self.is_active = True
                logger.info("🛡️ Anti-Spoofing Model đã được kích hoạt!")
            except Exception as e:
                logger.error(f"❌ Lỗi nạp model Anti-Spoofing: {e}")
        else:
            logger.warning(
                "⚠️ Chưa có model Anti-Spoofing (.onnx). Đang chạy ở chế độ [MOCK/GIẢ LẬP].")

    def analyze(self, frame, bbox, threshold=0.8):
        """
        Đánh giá khuôn mặt là THẬT (True) hay GIẢ MẠO (False).
        """
        # 1. Cắt khuôn mặt từ khung hình (có mở rộng lề một chút để lấy bối cảnh)
        x1, y1, x2, y2 = bbox.astype(int)
        h, w = frame.shape[:2]

        # Mở rộng (padding) lề 20% để model FAS nhìn thấy viền điện thoại (nếu có)
        pad_x = int((x2 - x1) * 0.2)
        pad_y = int((y2 - y1) * 0.2)

        nx1, ny1 = max(0, x1 - pad_x), max(0, y1 - pad_y)
        nx2, ny2 = min(w, x2 + pad_x), min(h, y2 + pad_y)

        face_crop = frame[ny1:ny2, nx1:nx2]

        # 2. KIỂM TRA MOCK (Nếu chưa có model)
        if not self.is_active:
            # Thuật toán chống cháy: Kiểm tra độ mờ (Blur) bằng Laplacian
            # (Thường ảnh in trên giấy hoặc chụp lại màn hình sẽ bị mờ/mất nét hơn mặt thật)
            gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Nếu mờ quá (score < 50), coi như ảnh giả
            is_real = blur_score > 50.0
            return is_real

        # 3. KIỂM TRA AI THẬT (Nếu có model ONNX)
        try:
            # Tiền xử lý ảnh (Resize về chuẩn của model FAS, ví dụ 80x80)
            face_resized = cv2.resize(face_crop, (80, 80))
            blob = cv2.dnn.blobFromImage(
                face_resized, 1.0, (80, 80), (0, 0, 0), swapRB=True, crop=False)

            # Chạy suy luận (Inference)
            inputs = {self.session.get_inputs()[0].name: blob}
            outputs = self.session.run(None, inputs)

            # Lấy điểm Liveness (Tùy model, giả sử index 1 là điểm Real)
            liveness_score = outputs[0][0][1]
            return liveness_score > threshold

        except Exception as e:
            logger.error(f"Lỗi khi check Liveness: {e}")
            return False


anti_spoof_service = AntiSpoofService()
