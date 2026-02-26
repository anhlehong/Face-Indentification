import cv2
import logging
from services.base import BaseService

logger = logging.getLogger(__name__)


class FaceService(BaseService):
    def extract_embedding(self, frame):
        faces = self.engine.detect_and_extract(frame)
        return faces[0].embedding if faces else None

    def detect_one_face(self, frame):
        return self.engine.detect_and_extract(frame, 1)

    def detect_faces(self, frame):
        return self.engine.detect_and_extract(frame, 0)

    def load_image(self, img_path: str):
        frame = cv2.imread(img_path)
        if frame is None:
            logger.error(f"Can't read image: {img_path}")
        return frame


face_service = FaceService()
