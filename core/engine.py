import logging
import threading
from insightface.app import FaceAnalysis
from config.settings import settings

logger = logging.getLogger(__name__)


class FaceEngine:
    def __init__(self):
        self._app = None
        self._lock = threading.Lock()

    def _ensure_model_loaded(self):
        """Hàm này đảm bảo model chỉ được load 1 lần duy nhất khi cần"""
        if self._app is None:
            with self._lock:
                if self._app is None:
                    logger.info(
                        f"🚀 Đang nạp Model AI: {settings.MODEL_NAME}...")
                    app = FaceAnalysis(name=settings.MODEL_NAME, root=".")
                    app.prepare(
                        ctx_id=settings.CTX_ID,
                        det_size=(settings.DET_SIZE, settings.DET_SIZE)
                    )
                    self._app = app
                    logger.info("✅ AI Engine đã sẵn sàng!")

    def detect_and_extract(self, frame):
        self._ensure_model_loaded()
        return self._app.get(frame)


face_engine = FaceEngine()
