import cv2
import threading
import time
from services.identity_service import identity_service


class CameraService:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Mở webcam
        self.frame = None
        self.is_running = False
        self._thread = None

    def start(self):
        """Khởi chạy luồng đọc camera độc lập"""
        self.is_running = True
        self._thread = threading.Thread(target=self._update, daemon=True)
        self._thread.start()

    def _update(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            time.sleep(0.01)  # Tránh chiếm dụng CPU quá mức

    def stop(self):
        self.is_running = False
        self.cap.release()


# Khởi tạo object dùng chung
camera_service = CameraService()
