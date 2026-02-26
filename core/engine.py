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
        if self._app is None:
            with self._lock:
                if self._app is None:
                    app = FaceAnalysis(
                        name=settings.MODEL_NAME,
                        root=".",
                        allowed_modules=['detection', 'recognition']
                    )
                    app.prepare(
                        ctx_id=settings.CTX_ID,
                        det_size=(settings.DET_SIZE, settings.DET_SIZE)
                    )
                    self._app = app
                    logger.info(
                        f"✅ AI Engine đã sẵn sàng với model {settings.MODEL_NAME}!")

    def quality_control(self, faces, frame_shape, min_face_size=80, min_score=0.6):
        valid_faces = []
        img_h, img_w = frame_shape[:2]

        for face in faces:
            if face.det_score < min_score:
                logger.debug(
                    f"⚠️ Bỏ qua khuôn mặt vì det_score quá thấp: {face.det_score}")
                continue

            bbox = face.bbox
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width < min_face_size or height < min_face_size:
                logger.debug(
                    f"⚠️ Bỏ qua khuôn mặt vì quá nhỏ: {width}x{height}")
                continue

            if bbox[0] < 0 or bbox[1] < 0 or bbox[2] > img_w or bbox[3] > img_h:
                logger.debug("⚠️ Bỏ qua khuôn mặt vì bị lẹm ở rìa ảnh.")
                continue

            valid_faces.append(face)

        return valid_faces

    # max_num = settings.MAX_FACE là số lượng khuôn mặt, = 0 là lấy hết.
    def detect_and_extract(self, frame, max_num=1, enforce_qc=True):

        self._ensure_model_loaded()
        faces = self._app.get(frame, max_num=max_num)

        if enforce_qc and faces:
            faces = self.quality_control(faces, frame.shape)

        return faces


face_engine = FaceEngine()
