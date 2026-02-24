import logging
from typing import List, Dict, Any
from services.identity_service import identity_service
from database.postgres import db_manager
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def display_results(results: List[Dict[str, Any]]) -> None:
    """Xử lý và hiển thị kết quả tìm kiếm khuôn mặt."""
    if not results:
        logger.info("Khong tim thay khuon mat nao trong anh.")
        return

    logger.info(f"Tim thay {len(results)} khuon mat:")

    for i, res in enumerate(results, 1):
        print(f"\n--- [Khuon mat {i}] ---")
        print(f"ID: {res.get('id')}")
        print(f"Ten: {res.get('name')}")
        print(f"Do tuong dong (Similarity): {res.get('similarity', 0):.4f}")
        print(f"Toa do mat (Box): {res.get('box')}")


def main():
    img_path = "data/images/taylor_swift/download.jpg"

    try:
        # Thuc hien tim kiem
        results = identity_service.search_face_by_path(img_path)

        # Hien thi ket qua
        display_results(results)

    except Exception as e:
        logger.error(f"Co loi xay ra: {e}")


if __name__ == "__main__":
    main()
