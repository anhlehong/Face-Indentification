import psycopg2
import sys

# THAY ĐỔI TẠI ĐÂY ĐỂ TEST
DB_URL = ""
if DB_URL is None or DB_URL.strip() == "":
    print("❌ Vui lòng điền DB_URL vào biến môi trường hoặc trực tiếp trong code.")
    sys.exit(1)


def test_connection():
    conn = None
    print(f"--- Đang thử kết nối tới: {DB_URL} ---")
    try:
        # Thêm timeout 5 giây để không bị treo máy
        conn = psycopg2.connect(DB_URL, connect_timeout=5)

        # Kiểm tra phiên bản Postgres
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()
        print(f"✅ Kết nối thành công!")
        print(f"🐘 Postgres Version: {db_version[0]}")

        # Kiểm tra pgvector
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        extension = cur.fetchone()
        if extension:
            print("✅ Tiện ích 'pgvector' đã được cài đặt.")
        else:
            print("⚠️ 'pgvector' chưa được cài đặt trong DB này.")

        cur.close()
    except psycopg2.OperationalError as e:
        print(f"❌ Lỗi kết nối (OperationalError): \n{e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: \n{e}")
    finally:
        if conn:
            conn.close()
            print("--- Đã đóng kết nối ---")


if __name__ == "__main__":
    test_connection()
