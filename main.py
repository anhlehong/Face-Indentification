import cv2
import logging
from services.camera_service import camera_service
from services.identity_service import identity_service
from services.visualizer_service import visualizer_service
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main():
    if not camera_service.start():
        return

    logger.info("✅ Hệ thống Identify đang chạy. Nhấn 'q' để thoát.")

    try:
        while True:
            # 1. Lấy frame từ luồng ngầm
            frame = camera_service.get_current_frame()
            if frame is None:
                continue

            # 2. Xử lý AI định danh (gọi đúng hàm process_frame)
            results = identity_service.process_frame(frame)

            # 3. Vẽ UI lên frame (gọi đúng hàm draw_frame)
            frame = visualizer_service.draw_frame(frame, results)

            # 4. Hiển thị
            cv2.imshow("Industrial Face Identify System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logger.info("Đang thoát chương trình...")
    finally:
        # Dọn dẹp tài nguyên an toàn
        camera_service.stop()
        cv2.destroyAllWindows()
        logger.info("🛑 Hệ thống đã dừng.")


if __name__ == "__main__":
    main()
