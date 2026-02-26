import cv2
import threading
import time
import logging

logger = logging.getLogger(__name__)


class CameraService:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.is_running = False

        self._thread = None
        self._lock = threading.Lock()

    def start(self) -> bool:
        if self.is_running:
            return True

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            logger.warning(
                f"⚠️ Không mở được camera index {self.camera_index}. Thử dùng DirectShow (DSHOW)...")
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            logger.error(
                "❌ Lỗi chí mạng: Không thể kết nối với bất kỳ Camera nào.")
            return False

        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.error(
                "❌ Kết nối được camera nhưng luồng hình ảnh bị trống.")
            self.cap.release()
            return False

        self.frame = frame
        self.is_running = True
        self._thread = threading.Thread(target=self._update, daemon=True)
        self._thread.start()
        logger.info("🎥 Camera Service đã khởi động thành công.")
        return True

    def _update(self):
        """Luồng chạy ngầm liên tục cập nhật khung hình mới nhất"""
        while self.is_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self._lock:
                        self.frame = frame
            time.sleep(0.01)

    def get_current_frame(self):
        """Getter an toàn cho các service khác lấy ảnh"""
        with self._lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """Dọn dẹp tài nguyên đa luồng an toàn"""
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        logger.info("🛑 Camera Service đã dừng an toàn.")


camera_service = CameraService()
