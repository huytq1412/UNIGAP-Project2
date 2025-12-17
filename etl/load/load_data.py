import json
import psycopg2
from psycopg2 import extras
import glob
import os

from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError

from config.config import load_config
from dotenv import load_dotenv


def get_db_connection():
    """Tạo kết nối đến PostgreSQL"""
    config = load_config()
    try:
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Lỗi kết nối mạng hoặc xác thực Database: {e}")
        return None
    except Exception as e:
        print(f"Lỗi không xác định khi kết nối DB: {e}")
        return None

def create_table():
    commands = (f"""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            url_key TEXT,
            price NUMERIC(15, 2),
            description TEXT
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS product_images (
            image_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
            base_url TEXT,
            large_url TEXT,
            medium_url TEXT,
            small_url TEXT,
            thumbnail_url TEXT,
            is_gallery BOOLEAN,
            label VARCHAR(255),
            position INTEGER
        )""")

    conn = get_db_connection()
    if conn is None:
        return

    try:
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)

            conn.commit()
            print("Đã tạo bảng thành công (trong trường hợp bảng chưa tồn tại)")
    except psycopg2.DatabaseError as e:
            print(f"Lỗi PostgreSQL khi tạo bảng: {e}")
            if conn: conn.rollback()
    except Exception as e:
        print(f"Lỗi hệ thống khi tạo bảng: {e}")
    finally:
        if conn: conn.close()

def insert_data(json_file_path):
    conn = get_db_connection()
    if conn is None:
        return

    if not os.path.exists(json_file_path):
        print(f"Thư mục '{json_file_path}' không tồn tại.")
        return

    files = glob.glob(os.path.join(json_file_path, "*.json"))

    try:
        with conn.cursor() as cur:
            count_number = 0

            for file in files:
                product_list = []
                product_id_list = []
                images_list = []

                with open(file,'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    # Xử lý bảng products
                    product_list.append((
                        item['id'],
                        item['name'],
                        item['url_key'],
                        item['price'],
                        item['description']
                    ))

                    product_id_list.append((item['id']))

                    # Xử lý bảng products_images
                    if item['images']:
                        for detail in item['images']:
                            images_list.append((
                                item['id'],
                                detail['base_url'],
                                detail['large_url'],
                                detail['medium_url'],
                                detail['small_url'],
                                detail['thumbnail_url'],
                                detail['is_gallery'],
                                detail['label'],
                                detail['position']
                            ))

                try:
                    if product_list:
                            insert_command = """
                                INSERT INTO products (product_id, name, url_key, price, description)
                                VALUES %s
                                ON CONFLICT (product_id) 
                                DO UPDATE SET
                                    name = EXCLUDED.name,
                                    url_key = EXCLUDED.url_key,
                                    price = EXCLUDED.price,
                                    description = EXCLUDED.description;
                            """
                            extras.execute_values(cur, insert_command, product_list, page_size=1000)

                    if images_list:
                        cur.execute('DELETE FROM product_images WHERE product_id = ANY(%s)', (product_id_list,))

                        insert_command = """
                            INSERT INTO product_images (product_id, base_url, large_url, medium_url,
                                                        small_url, thumbnail_url, is_gallery, label, position)
                            VALUES %s
                        """
                        extras.execute_values(cur, insert_command, images_list, page_size=1000)

                    count_number += len(product_list)

                    conn.commit()

                except DataError as e:
                    conn.rollback()
                    print(f"LỖI DỮ LIỆU (DataError)")
                    print(f"Lý do: Giá trị quá dài, sai kiểu số, hoặc chia cho 0. Chi tiết: {e.pgerror}")

                except IntegrityError as e:
                    conn.rollback()
                    print(f"LỖI RÀNG BUỘC (IntegrityError)")
                    print(f"Lý do: Vi phạm khóa ngoại. Chi tiết: {e.pgerror}")

                except OperationalError as e:
                    conn.rollback()
                    print(f"LỖI VẬN HÀNH (OperationalError)")
                    print(f"Lý do: Mất kết nối DB, DB đang restart, hoặc bị khóa (Deadlock). Chi tiết: {e}")
                    # Với lỗi này có thể cân nhắc break vòng lặp nếu DB chết hẳn

                except DatabaseError as e:
                    conn.rollback()
                    print(f"LỖI DATABASE CHUNG (DatabaseError). Chi tiết: {e}")

                except Exception as e:
                    conn.rollback()
                    print(f"LỖI KHÔNG XÁC ĐỊNH khi xử lý. Chi tiết: {e}")

            print(f"Xử lý xong tổng cộng {count_number} sản phẩm đã vào database.")

    except (psycopg2.DatabaseError,Exception) as e:
        print(f"Có lỗi xảy ra, đang Rollback: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Đã đóng kết nối.")

# Lấy thư mục file hiện tại
current_dir = os.path.dirname(__file__)

# Lấy thư mục gốc của project
project_dir = os.path.abspath(os.path.join(current_dir, '../..'))

# Lấy thư mục file .env
env_path = os.path.join(project_dir, '.env')

if __name__ == "__main__":
    create_table()

    load_dotenv(dotenv_path=env_path)

    json_file_path = os.environ.get('JSON_FILE_PATH')
    json_file_path = os.path.expanduser(json_file_path)

    insert_data(json_file_path)