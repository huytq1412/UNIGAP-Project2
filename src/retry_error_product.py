import pandas as pd
import os
from get_product import get_product_detail
from add_error import add_error_list
import concurrent.futures

def retry_error_product(client_errorfile, server_errorfile, error_file_path, json_file_path, agent):
    client_errorfile_temp = f"{error_file_path}/ErrorProduct_Client_temp.csv"
    additional_filename = f"{json_file_path}/ProductAdditonal.json"

    count_number = 1

    while True:
        # Điều kiện kết thúc vòng lặp
        # File lỗi từ phía client không còn tồn tại hoặc File lỗi có tồn tại, nhưng kích thước bằng 0
        if not os.path.exists(client_errorfile) or os.path.getsize(client_errorfile) == 0:
            # Xóa file lỗi từ phía client
            print(f"Không còn id trong danh sách lỗi từ client")
            if os.path.exists(client_errorfile):
                os.remove(client_errorfile)
            break
        # Vượt quá số lần thử lại cho phép
        elif count_number > 5:
            print(f"Đã vượt quá {count_number} lần thử lại, dừng crawl lại dữ liệu tại đây")
            break


        print(f"\n=== Bắt đầu crawl lại danh sách các id bị lỗi lần thứ {count_number} ===")

        # Xóa file temp nếu đã tồn tại
        if os.path.exists(client_errorfile_temp):
            os.remove(client_errorfile_temp)

        # Biến file lỗi từ client hiện tại thành file temp để lấy dữ liệu
        os.rename(client_errorfile, client_errorfile_temp)

        errorid_set = set()

        with open(client_errorfile_temp, 'r') as f:
            for line in f:
                line = line.strip()

                if line:
                    errorid_set.add(line)

        # Xóa file tạm
        if os.path.exists(client_errorfile_temp):
            os.remove(client_errorfile_temp)

        # Lấy tất cả product id do client lỗi
        errorid_list = list(errorid_set)

        product_detail_list = []  # List chứa thông tin các sản phẩm crawl dược
        server_error_list = []  # List các product id lỗi từ server
        client_error_list = []  # List các product id lỗi trong quá trình crawl dữ liệu

        # Default 15 threads to crawl data
        workers = 30

        # Sử dụng concurrent.futures để có nhiều luồng thu thập crawl dữ liệu hơn
        # Khởi tạo bể chứa các luồng
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Tạo một danh sách rỗng để chứa các đối tượng future
            list_futures = []

            # Duyệt qua từng id rồi thêm dữ liệu các future vào danh sách
            for id in errorid_list:
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

        if server_error_list:
            add_error_list(server_error_list, server_errorfile)

        if client_error_list:
            add_error_list(client_error_list, client_errorfile)

        # Lưu dữ liệu tất cả những product id được crawl lại vào một file duy nhất
        # Do chỉ lưu vào một file duy nhất -> gộp dữ liệu df cũ và df mới
        if product_detail_list:
            df_new = pd.DataFrame(product_detail_list)

            # Nếu đã tồn tại file -> gộp dữ liệu
            if os.path.exists(additional_filename):
                try:
                    # Lấy dữ liệu cũ đã có sẵn
                    df_old = pd.read_json(additional_filename)
                    # Gộp dữ liệu cũ và dữ liệu mới
                    df_errorid = pd.concat([df_old, df_new], ignore_index=True)
                except Exception as e:
                    df_errorid = df_new
            # Nếu chưa tồn tại file -> lấy luôn dữ liệu mới
            else:
                df_errorid = df_new

            df_errorid.to_json(additional_filename, orient='records', force_ascii=False, indent=4)

            print(f"Đã lưu dữ liệu vào: {additional_filename}")

        count_number += 1