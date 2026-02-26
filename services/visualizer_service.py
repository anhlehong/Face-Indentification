import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class VisualizerService:
    def __init__(self, font_path="arial.ttf"):
        # Load font chuẩn từ code cũ của bạn
        try:
            self.font_name = ImageFont.truetype(font_path, 24)
            self.font_info = ImageFont.truetype(font_path, 18)
        except:
            self.font_name = ImageFont.load_default()
            self.font_info = ImageFont.load_default()

    def _draw_utf8_text(self, draw, text, pos, color, font):
        """Logic vẽ chữ có viền (Outline) từ code cũ của bạn"""
        x, y = pos
        rgb_color = (color[2], color[1], color[0])  # BGR to RGB
        outline_color = (0, 0, 0)

        # Vẽ viền đen xung quanh để chữ nổi bật trên mọi nền
        draw.text((x-1, y-1), text, font=font, fill=outline_color)
        draw.text((x+1, y+1), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=rgb_color)

    def draw_frame(self, frame, results):
        """Hàm chính thực hiện vẽ mọi thành phần lên frame"""
        if not results:
            return frame

        # Chuyển frame sang PIL một lần duy nhất để tối ưu hiệu năng vẽ text
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        for person in results:
            x1, y1, x2, y2 = person['bbox']
            color = person['color']
            name = person['name']
            similarity = person.get('similarity', 0)
            kps = person.get('kps', [])

            # 1. Vẽ Bounding Box (Sử dụng OpenCV trực tiếp trên frame hoặc PIL)
            # Ở đây vẽ bằng PIL để đồng bộ layer
            shape = [x1, y1, x2, y2]
            draw.rectangle(shape, outline=tuple(color[::-1]), width=2)

            # 2. Vẽ Tên (Trên Box) - Tiếng Việt UTF-8
            self._draw_utf8_text(draw, name, (x1, y1 - 35),
                                 color, self.font_name)

            # 3. Vẽ Độ tương đồng (Dưới Box)
            sim_text = f"Sim: {similarity:.2f}"
            self._draw_utf8_text(draw, sim_text, (x1, y2 + 10),
                                 (255, 255, 255), self.font_info)

            # 4. Vẽ Hốc mắt và Keypoints
            if len(kps) > 0:
                for i, pt in enumerate(kps):
                    px, py = int(pt[0]), int(pt[1])
                    if i < 2:  # Mắt trái & Phải
                        # Vẽ vòng tròn hốc mắt rỗng (Cyan) và nhân đặc (Trắng)
                        draw.ellipse([px-6, py-6, px+6, py+6],
                                     outline=(0, 255, 255), width=1)
                        draw.ellipse([px-2, py-2, px+2, py+2],
                                     fill=(255, 255, 255))
                    else:  # Mũi, miệng
                        draw.ellipse([px-2, py-2, px+2, py+2],
                                     fill=(0, 255, 0))

        # Chuyển ngược lại OpenCV BGR
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


visualizer_service = VisualizerService()
