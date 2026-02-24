import cv2
from services.camera_service import camera_service
from services.identity_service import identity_service


def main():
    camera_service.start()
    print("🚀 Hệ thống Face ID đang chạy... Nhấn 'q' để thoát.")

    while True:
        frame = camera_service.frame
        if frame is None:
            continue

        # Nhận diện
        # Lưu ý: Ta gọi hàm nhận diện trực tiếp trên frame
        # (Để mượt hơn bạn có thể tối ưu chỉ nhận diện mỗi 5-10 frames)
        faces = identity_service.engine.detect_and_extract(frame)

        for face in faces:
            match = identity_service.repo.search_face(face.embedding)

            name = match['name'] if match else "Unknown"
            color = (0, 255, 0) if match else (0, 0, 255)

            # Vẽ
            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
            cv2.putText(frame, f"{name}", (box[0], box[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Face ID Industrial System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_service.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
