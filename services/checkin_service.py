import time
import logging
from services.identity_service import identity_service

logger = logging.getLogger(__name__)


class CheckInService:
    def __init__(self):
        self.identity = identity_service
        self.process_interval = 5
        self.frame_count = 0
        self.cached_results = []

        # Cấu hình nghiệp vụ
        self.COOLDOWN_TIME = 60 * 2  # Thời gian đóng băng 2 phút
        self.REQUIRED_HITS = 2       # Số frame liên tiếp cần thiết để chốt check-in

        self.recent_checkins = {}
        self.hit_counters = {}

    def _process_checkin_logic(self, match: dict):
        user_id = match['id']
        name = match['name']

        # 1. Trong thời gian chờ (Đã check-in rồi) -> Màu Xanh Lá
        if user_id in self.recent_checkins:
            if time.time() - self.recent_checkins[user_id] < self.COOLDOWN_TIME:
                return name, (0, 255, 0), "Already Checked-in"  # Green

        self.hit_counters[user_id] = self.hit_counters.get(user_id, 0) + 1

        # 2. Đang trong quá trình xác nhận -> Màu Xanh Lá
        if self.hit_counters[user_id] < self.REQUIRED_HITS:
            return name, (0, 255, 0), "Verifying..."  # Green

        # 3. CHỐT CHECK-IN -> Màu Xanh Dương (OpenCV dùng BGR: Blue là 255, 0, 0)
        logger.info(f"🎉 SUCCESS: {name} has successfully checked in.")

        self.recent_checkins[user_id] = time.time()
        self.hit_counters[user_id] = 0

        return name, (255, 0, 0), "CHECK-IN SUCCESS"  # Blue

    def process_frame(self, frame):
        self.frame_count += 1

        # Frame Skipping: Bỏ nhịp để tăng FPS
        if self.frame_count % self.process_interval == 0:
            faces = self.identity.engine.detect_and_extract(frame)
            new_results = []
            current_ids = set()

            for face in faces:
                match = self.identity.repo.search_face(face.embedding)
                box = face.bbox.astype(int).tolist()

                if match:
                    current_ids.add(match['id'])
                    name, color, status = self._process_checkin_logic(match)
                    new_results.append(
                        {"box": box, "name": name, "color": color, "status": status})
                else:
                    # Không nhận diện được -> Màu Đỏ
                    new_results.append({"box": box, "name": "Unknown", "color": (
                        0, 0, 255), "status": "Unregistered"})

            # Reset bộ đếm cho những user đã rời khỏi khung hình
            for uid in list(self.hit_counters.keys()):
                if uid not in current_ids:
                    self.hit_counters[uid] = 0

            self.cached_results = new_results

        return self.cached_results


# Export module-level object
checkin_service = CheckInService()
