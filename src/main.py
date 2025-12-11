from dotenv import load_dotenv
import pandas as pd
import os
from get_product import get_product_detail
from add_error import add_error_list
from retry_error_product import  retry_error_product
from fake_useragent import UserAgent
import concurrent.futures
import time
import datetime

# Lấy thư mục file hiện tại
current_dir = os.path.dirname(__file__)

# Lấy thư mục gốc của project
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Lấy thư mục file .env
env_path = os.path.join(project_dir, '.env')

if __name__ == '__main__':
    load_dotenv(dotenv_path=env_path)

    json_file_path = os.environ.get('JSON_FILE_PATH')
    json_file_path = os.path.expanduser(json_file_path)

    error_file_path = os.environ.get('ERROR_FILE_PATH')
    error_file_path = os.path.expanduser(error_file_path)

    data_path = os.environ.get('DATA_PATH')
    data_path = os.path.expanduser(data_path)
    data_path = f'{data_path}/products-0-200000.csv'

    if not os.path.exists(json_file_path):
        os.makedirs(json_file_path)

    if not os.path.exists(error_file_path):
        os.makedirs(error_file_path)

    server_errorfile = f"{error_file_path}/ErrorProduct_Server.csv"
    client_errorfile = f"{error_file_path}/ErrorProduct_Client.csv"

    try:
        reader = pd.read_csv(data_path, dtype=str, chunksize=1000)
    except FileNotFoundError:
        print(f"Không tìm thấy file {data_path}")
        exit()

    agent = UserAgent()

    start_time = time.time()

    for idx, df_chunk in enumerate(reader):
        # if idx >= 3:
        #     print(f"--- Đã kiểm tra {idx} batch, dừng chương trình ---")
        #     break
        #
        # if idx == 2:
        #     print(f"--- Đang giả lập lỗi nghiêm trọng để test Restart ---")
        #     raise Exception("Lỗi giả định do người dùng tạo!")

        chunk_number = idx + 1

        filename = f"{json_file_path}/ProductBatch{chunk_number}.json"

        # Kiểm tra nếu file đã tồn tại thì bỏ qua
        if os.path.exists(filename):
            print(f"Batch {chunk_number} đã tồn tại. Bỏ qua.")
            continue

        product_detail_list = [] # List chứa thông tin các sản phẩm crawl dược
        server_error_list = [] # List các product id lỗi từ server
        client_error_list = [] # List các product id lỗi trong quá trình crawl dữ liệu

        print(f"--- Đang xử lý batch {chunk_number} ---")

        # Mặc định 30 luồng để crawl dữ liệu
        workers = 30

        # Sử dụng concurrent.futures để có nhiều luồng thu thập crawl dữ liệu hơn
        # Khởi tạo bể chứa các luồng
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Tạo một danh sách rỗng để chứa các đối tượng future
            list_futures = []

            # Duyệt qua từng id của batch hiện tại rồi thêm dữ liệu các future vào danh sách
            for id in df_chunk['id']:
                future = executor.submit(get_product_detail, id, agent)

                list_futures.append(future)

            # Duyệt qua danh sách các future, as_completed sẽ đợi và nhả ra các future ngay khi nó hoàn thành
            for future in concurrent.futures.as_completed(list_futures):
                product_data, error_id_server, error_id_client = future.result()

                if product_data:
                    product_detail_list.append(product_data)
                elif error_id_server:
                    server_error_list.append(error_id_server)
                elif error_id_client:
                    client_error_list.append(error_id_client)

        if product_detail_list:
            df = pd.DataFrame(product_detail_list)

            df.to_json(filename, orient='records', force_ascii=False, indent=4)

            elapsed_seconds = int(time.time() - start_time)

            elapsed_readable = datetime.timedelta(seconds=elapsed_seconds)

            print(f"Đã lưu dữ liệu vào: {filename}. Tổng thời gian đã chạy: {elapsed_readable}")
        else:
            print(f"-> Batch {chunk_number} không có dữ liệu.")

        if server_error_list:
            add_error_list(server_error_list, server_errorfile)

            print(f"Đã lưu các bản ghi lỗi vào: {server_errorfile}")

        if client_error_list:
            add_error_list(client_error_list, client_errorfile)

            print(f"Đã lưu các bản ghi lỗi vào: {client_errorfile}")

    # Crawl lại dữ liệu danh sách các id bị lỗi từ phía client
    retry_error_product(client_errorfile, server_errorfile, error_file_path, json_file_path, agent)