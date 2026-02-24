import cv2
import time
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from services.camera_service import camera_service
from services.checkin_service import checkin_service
from database.postgres import db_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class FaceIDApplication:
    def __init__(self):
        self.window_name = "Face ID System"
        self.prev_time = time.time()

        # Load font để hỗ trợ hiển thị tên Tiếng Việt (UTF-8) từ Database
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
            self.font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            self.font = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def _draw_utf8_text(self, img, text, pos, color, font):
        """Hàm phụ trợ vẽ text chuẩn UTF-8 sử dụng Pillow"""
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # Chuyển BGR (OpenCV) sang RGB (Pillow)
        rgb_color = (color[2], color[1], color[0])
        x, y = pos

        # Vẽ viền chữ (Outline) màu đen giúp dễ đọc trên mọi nền sáng/tối
        outline_color = (0, 0, 0)
        draw.text((x-1, y-1), text, font=font, fill=outline_color)
        draw.text((x+1, y+1), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=rgb_color)

        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def startup(self) -> bool:
        if not camera_service.start():
            return False
        return True

    def run(self):
        if not self.startup():
            return

        logger.info(
            "✅ System is running. Press 'q' on the camera window to exit.")

        while True:
            frame = camera_service.get_current_frame()
            if frame is None:
                continue

            # Xử lý logic check-in
            draw_data = checkin_service.process_frame(frame)

            # Vẽ UI
            for data in draw_data:
                box, color, name, status = data["box"], data["color"], data["name"], data["status"]
                x1, y1, x2, y2 = box

                # Vẽ Box khuôn mặt
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Vẽ tên người (hỗ trợ Tiếng Việt) ở trên Box
                frame = self._draw_utf8_text(
                    frame, name, (x1, y1 - 35), color, self.font)

                # Vẽ trạng thái (English) ở dưới Box
                if status:
                    frame = self._draw_utf8_text(
                        frame, status, (x1, y2 + 10), (255, 255, 255), self.font_small)

            # Tính toán và hiển thị FPS
            curr_time = time.time()
            fps = 1 / (curr_time - self.prev_time)
            self.prev_time = curr_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 0), 1)

            cv2.imshow(self.window_name, frame)

            # Thoát ứng dụng
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("🛑 Exiting application...")
                break

        self.shutdown()

    def shutdown(self):
        camera_service.stop()
        cv2.destroyAllWindows()
        db_manager.close_all()


if __name__ == "__main__":
    app = FaceIDApplication()
    app.run()
