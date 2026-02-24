import numpy as np
from database.user_repository import user_repo
from entities.user import User


def main():
    # Tạo vector giả
    vec = np.random.rand(512)
    vec /= np.linalg.norm(vec)

    # Dùng trực tiếp user_repo đã được import
    user_repo.add_user(User(full_name="Anh Le", embedding=vec))

    result = user_repo.search_face(vec)
    print(f"Tìm thấy: {result['name']} với độ khớp {result['similarity']:.2f}")


if __name__ == "__main__":
    main()
